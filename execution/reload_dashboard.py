import json
import urllib.request
import sys

# We can use standard urllib to send the CDP payload to avoid missing websocket-client dependency!
# Actually, CDP requires websockets for Page.reload. We'll try the local hermes venv.
try:
    import websocket
except ImportError:
    print("websocket-client not found, can't reload via CDP")
    sys.exit(1)

def reload_dashboard():
    try:
        req = urllib.request.Request("http://127.0.0.1:9222/json")
        with urllib.request.urlopen(req) as response:
            tabs = json.loads(response.read())

        for tab in tabs:
            if tab.get("url", "").startswith("http://127.0.0.1:9120"):
                ws_url = tab.get("webSocketDebuggerUrl")
                if ws_url:
                    ws = websocket.create_connection(ws_url)
                    ws.send(json.dumps({
                        "id": 1,
                        "method": "Page.reload",
                        "params": {"ignoreCache": True}
                    }))
                    ws.close()
                    print(f"Reloaded dashboard tab: {tab.get('title')}")
                    return
        print("Dashboard tab not found to reload.")
    except Exception as e:
        print(f"Failed to reload via CDP: {e}")

if __name__ == "__main__":
    reload_dashboard()
