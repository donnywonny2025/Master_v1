import urllib.request
import json
import time

def enforce_raw_cdp_hygiene():
    try:
        req = urllib.request.Request("http://localhost:9222/json/list")
        with urllib.request.urlopen(req) as resp:
            tabs = json.loads(resp.read().decode('utf-8'))
            
        kept_flow = False
        
        for tab in tabs:
            tab_type = tab.get("type", "")
            title = tab.get("title", "").lower()
            url = tab.get("url", "").lower()
            target_id = tab.get("id")
            
            if tab_type == "page" and not url.startswith("devtools://"):
                if not kept_flow and ("flow" in title or "labs.google" in url):
                    kept_flow = True
                    print(f"✅ PROTECTED MAIN HUB: {tab.get('title')} ({url})")
                    # Try to bring it to front
                    urllib.request.urlopen(f"http://localhost:9222/json/activate/{target_id}")
                else:
                    print(f"🚫 TERMINATING DUPLICATE: {tab.get('title')} ({url})")
                    urllib.request.urlopen(f"http://localhost:9222/json/close/{target_id}")
                    time.sleep(0.5)
                    
        print("\nSweep Complete.")
    except Exception as e:
        print(f"Fatal Error: {e}")

if __name__ == "__main__":
    enforce_raw_cdp_hygiene()
