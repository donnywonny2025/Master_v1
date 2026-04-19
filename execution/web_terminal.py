import tornado.web
import tornado.ioloop
import terminado
import os
import sys

# Define the command to run in the terminal
cmd = ["bash"]

# Create a terminal manager
term_manager = terminado.SingleTermManager(shell_command=cmd)

# Define the simple HTML template for xterm.js
class TerminalPageHandler(tornado.web.RequestHandler):
    def get(self):
        HTML = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Hermes Web Terminal</title>
            <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500&display=swap" rel="stylesheet">
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/xterm@4.19.0/css/xterm.css" />
            <script src="https://cdn.jsdelivr.net/npm/xterm@4.19.0/lib/xterm.js"></script>
            <script src="https://cdn.jsdelivr.net/npm/xterm-addon-fit@0.5.0/lib/xterm-addon-fit.js"></script>
            <style>
                * { box-sizing: border-box; }
                body { 
                    margin: 0; 
                    padding: 0;
                    background: #050505;
                    background-image: radial-gradient(circle at 50% 0%, #111111 0%, #000000 70%);
                    font-family: 'Inter', sans-serif; 
                    height: 100vh;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: flex-start;
                    padding-top: 6vh;
                    color: #fff;
                    overflow: hidden;
                }
                .header {
                    text-align: center;
                    margin-bottom: 28px;
                    animation: fadeIn 1.2s ease-out;
                }
                .header h1 {
                    font-weight: 400;
                    font-size: 0.9rem;
                    color: #ffffff;
                    margin: 0;
                    letter-spacing: 12px;
                    text-transform: uppercase;
                }
                .header p {
                    color: #525252;
                    font-size: 0.7rem;
                    margin-top: 14px;
                    font-weight: 300;
                    letter-spacing: 4px;
                    text-transform: uppercase;
                }
                .terminal-wrapper {
                    width: 1050px;
                    max-width: 95vw;
                    height: 700px;
                    background: #09090b;
                    border: 1px solid #1f1f1f;
                    border-radius: 6px;
                    box-shadow: 0 40px 80px -20px rgba(0,0,0,0.8);
                    display: flex;
                    flex-direction: column;
                    overflow: hidden;
                    animation: fadeInUp 1s cubic-bezier(0.16, 1, 0.3, 1) forwards;
                    opacity: 0;
                    transform: translateY(20px);
                }
                .top-bar {
                    height: 44px;
                    background: #0c0c0e;
                    border-bottom: 1px solid #1a1a1a;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    padding: 0 16px;
                }
                .top-title {
                    color: #52525b;
                    font-size: 0.75rem;
                    font-weight: 400;
                    letter-spacing: 1.5px;
                }
                #terminal-container { 
                    flex: 1;
                    padding: 24px 0;
                    margin: 0 28px;
                    overflow: hidden;
                }
                .xterm .xterm-viewport { background-color: transparent !important; }
                
                /* Custom Cinematic Scrollbar Override */
                .xterm-viewport::-webkit-scrollbar {
                    width: 8px;
                }
                .xterm-viewport::-webkit-scrollbar-track {
                    background: #09090b; 
                    border-left: 1px solid #1f1f1f;
                }
                .xterm-viewport::-webkit-scrollbar-thumb {
                    background: #27272a; 
                    border-radius: 4px;
                    border: 2px solid #09090b; /* Adds padding effect */
                }
                .xterm-viewport::-webkit-scrollbar-thumb:hover {
                    background: #3f3f46; 
                }
                
                @keyframes fadeIn {
                    from { opacity: 0; }
                    to { opacity: 1; }
                }
                @keyframes fadeInUp {
                    to { opacity: 1; transform: translateY(0); }
                }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>HERMES NEXUS</h1>
                <p>System Architecture Engine</p>
            </div>
            <div class="terminal-wrapper">
                <div class="top-bar">
                    <div class="top-title">bash — hermes-agent</div>
                </div>
                <div id="terminal-container"></div>
            </div>
            <script>
                var term = new Terminal({
                    cursorBlink: true,
                    theme: { background: 'transparent', foreground: '#e4e4e7', cursor: '#71717a', selection: 'rgba(255,255,255,0.15)' },
                    fontSize: 14,
                    fontFamily: '"SF Mono", Menlo, Monaco, "Courier New", monospace',
                    allowTransparency: true
                });
                var fitAddon = new FitAddon.FitAddon();
                term.loadAddon(fitAddon);
                term.open(document.getElementById('terminal-container'));

                setTimeout(() => {
                    fitAddon.fit();
                    connectPty();
                }, 100);

                function connectPty() {
                    var ws_url = "ws://" + location.host + "/websocket";
                    var ws = new WebSocket(ws_url);

                    ws.onopen = function(event) {
                        term.onData(function(data) {
                            ws.send(JSON.stringify(['stdin', data]));
                        });
                        ws.send(JSON.stringify(['set_size', term.rows, term.cols, window.innerWidth, window.innerHeight]));
                    };

                    ws.onmessage = function(event) {
                        var msg = JSON.parse(event.data);
                        if (msg[0] === 'stdout') {
                            term.write(msg[1]);
                        }
                    };
                    
                    window.addEventListener('resize', function() {
                        fitAddon.fit();
                        if (ws.readyState === WebSocket.OPEN) {
                            ws.send(JSON.stringify(['set_size', term.rows, term.cols, window.innerWidth, window.innerHeight]));
                        }
                    });
                }
            </script>
        </body>
        </html>
        """
        self.write(HTML)

def main():
    handlers = [
        (r"/", TerminalPageHandler),
        (r"/websocket", terminado.TermSocket, {'term_manager': term_manager})
    ]
    app = tornado.web.Application(handlers)
    app.listen(9119) # Arbitrary port
    print("Hermes Web Terminal Server started successfully on http://127.0.0.1:9119")
    print("Keep this process running, and open that URL in Chrome.")
    tornado.ioloop.IOLoop.current().start()

if __name__ == "__main__":
    main()
