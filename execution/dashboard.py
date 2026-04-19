import tornado.web
import tornado.ioloop
import tornado.websocket
import terminado
import os
import sys
import json
import time
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

main_loop = None

# --- 1. Event Broker for WebSockets ---
class EventBroker:
    def __init__(self):
        self.clients = set()

    def add_client(self, client):
        self.clients.add(client)

    def remove_client(self, client):
        self.clients.remove(client)

    def broadcast(self, message):
        # WebSocket writes are NOT thread-safe in Tornado. 
        # File watcher and Log tailer run in background threads, 
        # so we MUST post the write back to the main IOLoop global instance.
        if main_loop:
            main_loop.add_callback(self._do_broadcast, message)
        
    def _do_broadcast(self, message):
        for client in list(self.clients):
            try:
                client.write_message(json.dumps(message))
            except Exception:
                self.clients.remove(client)

broker = EventBroker()

# --- 2. WebSocket Handler for Events ---
class EventHandler(tornado.websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True

    def open(self):
        broker.add_client(self)
        self.write_message(json.dumps({"type": "status", "data": "Connected to Event Stream..."}))

    def on_close(self):
        broker.remove_client(self)

# --- 3. Watchdog File System Events ---
class WorkspaceChangeHandler(FileSystemEventHandler):
    def process_event(self, event, event_type):
        if event.is_directory or "/.git/" in event.src_path or "/.tmp/" in event.src_path or "/node_modules/" in event.src_path:
            return
        # Make the path relative to make it clean
        rel_path = os.path.relpath(event.src_path, start=os.getcwd())
        broker.broadcast({"type": "file_event", "action": event_type, "file": rel_path})

    def on_modified(self, event):
        self.process_event(event, "MODIFIED")
    
    def on_created(self, event):
        self.process_event(event, "CREATED")

    def on_deleted(self, event):
        self.process_event(event, "DELETED")

def start_file_watcher():
    observer = Observer()
    observer.schedule(WorkspaceChangeHandler(), ".", recursive=True)
    observer.start()

# --- 4. Tail the Agent Log ---
def tail_agent_log():
    log_file = ".agent_activity.log"
    # Ensure it exists
    if not os.path.exists(log_file):
        open(log_file, "a").close()

    with open(log_file, "r") as f:
        # Seek to the end immediately
        f.seek(0, 2)
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.1)
                continue
            broker.broadcast({"type": "agent_log", "data": line.strip()})

# --- 5. Main Dashboard View ---
class DashboardPageHandler(tornado.web.RequestHandler):
    def get(self):
        # We inline standard xterm terminal alongside an event list
        HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Hermes Command Center</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/xterm@4.19.0/css/xterm.css" />
    <script src="https://cdn.jsdelivr.net/npm/xterm@4.19.0/lib/xterm.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/xterm-addon-fit@0.5.0/lib/xterm-addon-fit.js"></script>
    <style>
        :root {
            --bg-deep: #050505;
            --bg-panel: #09090b;
            --border-color: #27272a;
            --accent: #e4e4e7;
            --text-muted: #a1a1aa;
        }
        * { box-sizing: border-box; }
        body { 
            margin: 0; padding: 0;
            background: var(--bg-deep);
            color: var(--accent);
            font-family: 'Inter', sans-serif;
            height: 100vh;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        .header {
            padding: 16px 24px;
            border-bottom: 1px solid var(--border-color);
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: rgba(0, 0, 0, 0.4);
            backdrop-filter: blur(10px);
        }
        .header h1 {
            margin: 0; font-size: 1rem; font-weight: 500; letter-spacing: 2px;
            color: #fff;
        }
        .status-indicator {
            display: flex; align-items: center; gap: 8px; font-size: 0.8rem; color: #10b981;
        }
        .status-dot { width: 8px; height: 8px; background: #10b981; border-radius: 50%; box-shadow: 0 0 8px #10b981; }

        .container {
            flex: 1;
            display: flex;
            flex-direction: column;
            padding: 24px;
            gap: 24px;
            height: calc(100vh - 60px);
        }

        /* Top Panel - Terminal */
        .terminal-panel {
            flex: 5;
            background: var(--bg-panel);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            display: flex;
            flex-direction: column;
            overflow: hidden;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        }
        .panel-header {
            padding: 10px 16px; background: #111113; border-bottom: 1px solid var(--border-color);
            font-size: 0.75rem; letter-spacing: 1px; color: var(--text-muted);
            text-transform: uppercase; display: flex; justify-content: space-between;
        }
        #terminal-wrap {
            flex: 1; padding: 16px; overflow: hidden;
        }
        
        /* Bottom Panel - Activity Feed */
        .activity-panel {
            flex: 3;
            background: var(--bg-panel);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            display: flex;
            flex-direction: column;
            overflow: hidden;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        }
        #activity-feed {
            flex: 1; padding: 16px; overflow-y: auto;
            font-family: "SF Mono", Menlo, Monaco, "Courier New", monospace;
            font-size: 0.8rem; line-height: 1.6;
        }
        .entry { opacity: 0; animation: slideIn 0.3s forwards; padding-bottom: 4px; border-bottom: 1px solid rgba(255,255,255,0.05); margin-bottom: 4px; }
        .entry-time { color: #52525b; margin-right: 8px; }
        .entry-type { font-weight: 600; margin-right: 8px; padding: 2px 6px; border-radius: 4px; font-size: 0.7rem; }
        
        .type-file { color: #3b82f6; background: rgba(59, 130, 246, 0.1); }
        .type-agent { color: #8b5cf6; background: rgba(139, 92, 246, 0.1); }
        
        .entry-text { color: #d4d4d8; }

        @keyframes slideIn { from { opacity: 0; transform: translateY(5px); } to { opacity: 1; transform: translateY(0); } }

        /* Custom Scrollbar */
        ::-webkit-scrollbar { width: 8px; }
        ::-webkit-scrollbar-track { background: var(--bg-panel); }
        ::-webkit-scrollbar-thumb { background: #3f3f46; border-radius: 4px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>HERMES COMMAND CENTER</h1>
        <div class="status-indicator"><div class="status-dot"></div> Live</div>
    </div>
    
    <div class="container">
        <!-- Terminal Panel -->
        <div class="terminal-panel">
            <div class="panel-header">Interactive Shell</div>
            <div id="terminal-wrap"></div>
        </div>

        <!-- Activity Panel -->
        <div class="activity-panel">
            <div class="panel-header">
                <span>System Activity Feed</span>
                <span id="feed-status" style="color: #10b981;">● Connected</span>
            </div>
            <div id="activity-feed"></div>
        </div>
    </div>

    <script>
        // Terminal Setup
        const term = new Terminal({
            theme: { background: 'transparent', foreground: '#e4e4e7', cursor: '#71717a' },
            fontFamily: '"SF Mono", Menlo, Monaco, "Courier New", monospace',
            fontSize: 14
        });
        const fitAddon = new FitAddon.FitAddon();
        term.loadAddon(fitAddon);
        term.open(document.getElementById('terminal-wrap'));

        setTimeout(() => {
            fitAddon.fit();
            connectPty();
            connectEvents();
        }, 100);

        function connectPty() {
            const ws = new WebSocket("ws://" + location.host + "/terminal");
            ws.onopen = () => {
                term.onData(data => ws.send(JSON.stringify(['stdin', data])));
                ws.send(JSON.stringify(['set_size', term.rows, term.cols, window.innerWidth, window.innerHeight]));
            };
            ws.onmessage = e => {
                const msg = JSON.parse(e.data);
                if (msg[0] === 'stdout') term.write(msg[1]);
            };
            window.addEventListener('resize', () => {
                fitAddon.fit();
                if (ws.readyState === WebSocket.OPEN) {
                    ws.send(JSON.stringify(['set_size', term.rows, term.cols, window.innerWidth, window.innerHeight]));
                }
            });
        }

        // Activity Feed Setup
        function connectEvents() {
            const ws = new WebSocket("ws://" + location.host + "/events");
            const feed = document.getElementById('activity-feed');
            
            function appendLog(typeClass, label, text) {
                const time = new Date().toLocaleTimeString([], {hour12: false});
                const div = document.createElement('div');
                div.className = 'entry';
                div.innerHTML = `<span class="entry-time">[${time}]</span><span class="entry-type ${typeClass}">${label}</span><span class="entry-text">${text}</span>`;
                feed.appendChild(div);
                feed.scrollTop = feed.scrollHeight;
            }

            ws.onmessage = e => {
                const data = JSON.parse(e.data);
                if (data.type === 'file_event') {
                    appendLog('type-file', data.action, data.file);
                } else if (data.type === 'agent_log') {
                    appendLog('type-agent', 'AGENT', data.data);
                } else if (data.type === 'status') {
                    appendLog('type-agent', 'SYSTEM', data.data);
                }
            };
            
            ws.onclose = () => {
                document.getElementById('feed-status').style.color = '#ef4444';
                document.getElementById('feed-status').innerText = '● Disconnected';
            }
        }
    </script>
</body>
</html>
"""
        self.write(HTML)

def main():
    global main_loop
    main_loop = tornado.ioloop.IOLoop.current()

    # 1. Start File Watcher
    start_file_watcher()
    
    # 2. Start Log Tailer
    threading.Thread(target=tail_agent_log, daemon=True).start()

    # 3. Setup Terminal
    cmd = ["bash", "-c", "cd execution/hermes-agent && exec .venv/bin/hermes chat"]
    term_manager = terminado.SingleTermManager(shell_command=cmd)

    # 4. Web Application Routes
    handlers = [
        (r"/", DashboardPageHandler),
        (r"/terminal", terminado.TermSocket, {'term_manager': term_manager}),
        (r"/events", EventHandler)
    ]
    
    app = tornado.web.Application(handlers)
    app.listen(9120)
    print("Hermes Command Center available at http://127.0.0.1:9120")
    
    tornado.ioloop.IOLoop.current().start()

if __name__ == "__main__":
    main()
