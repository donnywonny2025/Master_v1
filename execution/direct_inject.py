import asyncio
import websockets
import json
import sys

async def inject_msg(msg):
    uri = "ws://127.0.0.1:9120/terminal"
    try:
        async with websockets.connect(uri) as ws:
            # We must send standard carriage return for the enter key
            payload = json.dumps(["stdin", msg + "\r"])
            await ws.send(payload)
            # Give it a fraction of a second to flush
            await asyncio.sleep(0.1)
    except Exception as e:
        print(f"Injection failed: {e}")

if __name__ == "__main__":
    asyncio.run(inject_msg(" ".join(sys.argv[1:])))
