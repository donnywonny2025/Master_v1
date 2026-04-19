import asyncio
import websockets
import json
import logging
import sys

# Set up logging to silence warnings
logging.getLogger("websockets").setLevel(logging.CRITICAL)

async def monitor_terminal():
    uri = "ws://127.0.0.1:9120/terminal"
    try:
        async with websockets.connect(uri) as ws:
            with open(".terminal_transcript.log", "w", encoding="utf-8") as f:
                f.write("--- INTERNAL TERMINAL TRANSCRIPT STARTED ---\n")
                while True:
                    msg = await ws.recv()
                    try:
                        data = json.loads(msg)
                        if isinstance(data, list) and len(data) >= 2 and data[0] == "stdout":
                            # The data is raw PTY stdout containing ANSI escape sequences
                            f.write(data[1])
                            f.flush()
                    except json.JSONDecodeError:
                        pass
    except Exception as e:
        print(f"Monitor error: {e}")

if __name__ == "__main__":
    asyncio.run(monitor_terminal())
