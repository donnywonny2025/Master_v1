import asyncio
import websockets
import json
import urllib.request

async def reload_dashboard():
    # Fetch active targets
    req = urllib.request.Request("http://127.0.0.1:9222/json")
    with urllib.request.urlopen(req) as response:
        targets = json.loads(response.read().decode())
    
    for target in targets:
        if "127.0.0.1:9120" in target.get("url", ""):
            ws_url = target.get("webSocketDebuggerUrl")
            if ws_url:
                async with websockets.connect(ws_url) as ws:
                    msg = {"id": 1, "method": "Page.reload", "params": {"ignoreCache": True}}
                    await ws.send(json.dumps(msg))
                    print("Reloaded dashboard!")
                    return
    print("Dashboard tab not found.")

asyncio.run(reload_dashboard())
