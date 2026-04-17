import asyncio
import json
import os
import sys
import time
from urllib.parse import urlparse
from playwright.async_api import async_playwright

MAPS_DIR = os.path.join(os.getcwd(), "knowledgebase", "maps")

async def extract_map():
    start_time = time.time()
    async with async_playwright() as p:
        try:
            browser = await p.chromium.connect_over_cdp("http://localhost:9222")
            
            # Find the active webpage
            target_page = None
            # Walk backwards so we get the most recently opened real tab
            for context in browser.contexts:
                for page in reversed(context.pages):
                    if not page.url.startswith("chrome://") and not page.url.startswith("about:"):
                        target_page = page
                        break
                if target_page:
                    break
            
            if not target_page:
                print("No active page found to map.")
                await browser.close()
                return

            print(f"Mapping geometry for: {target_page.url}")
            
            # Generate a safe filename based on the domain
            parsed_url = urlparse(target_page.url)
            domain = parsed_url.netloc.replace("www.", "")
            if not domain:
                domain = "local_page"
            filename = f"{domain}_map.json"
            filepath = os.path.join(MAPS_DIR, filename)

            # Inject JS to harvest the bounding rectangles of interactive elements
            js_payload = """
            () => {
                const elements = Array.from(document.querySelectorAll('button, a, input, select, textarea, [role="button"], canvas'));
                let map = [];
                elements.forEach(el => {
                    const rect = el.getBoundingClientRect();
                    // Only map elements that actually have physical dimensions on screen
                    if (rect.width > 0 && rect.height > 0) {
                        map.push({
                            tag: el.tagName.toLowerCase(),
                            text: el.innerText ? el.innerText.trim().substring(0, 50) : '',
                            id: el.id || '',
                            x: Math.round(rect.x),
                            y: Math.round(rect.y),
                            width: Math.round(rect.width),
                            height: Math.round(rect.height)
                        });
                    }
                });
                return map;
            }
            """
            
            dom_map = await target_page.evaluate(js_payload)
            
            # Save the JSON file permanently
            os.makedirs(MAPS_DIR, exist_ok=True)
            with open(filepath, "w") as f:
                json.dump({"url": target_page.url, "viewport": target_page.viewport_size, "elements": dom_map}, f, indent=2)
            
            elapsed = int((time.time() - start_time) * 1000)
            print(f"Successfully mapped {len(dom_map)} elements to {filename} in {elapsed} milliseconds!")
            
            await browser.close()
            
        except Exception as e:
            print(f"FATAL Mapper Error: {e}")
            sys.exit(1)

if __name__ == "__main__":
    asyncio.run(extract_map())
