import sys
import time

msg = sys.argv[1] if len(sys.argv) > 1 else "Testing log feed..."
with open(".agent_activity.log", "a") as f:
    f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")
    print(f"Wrote to log: {msg}")
