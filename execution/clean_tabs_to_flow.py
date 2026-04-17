import asyncio
from playwright.async_api import async_playwright

async def clean_tabs_and_focus_flow():
    async with async_playwright() as p:
        try:
            print("Connecting to AMOS Browser...")
            browser = await p.chromium.connect_over_cdp("http://localhost:9222")
            
            flow_tab_kept = False
            
            for context in browser.contexts:
                pages = context.pages
                for page in pages:
                    url = page.url.lower()
                    title = page.title()
                    
                    if not flow_tab_kept and ("flow" in url or "labs.google" in url):
                        flow_tab_kept = True
                        print(f"Keeping Primary Flow Tab: {url}")
                        await page.bring_to_front()
                    else:
                        print(f"Closing Duplicate/Junk Tab: {title} ({url})")
                        await page.close()

            print("Tab cleanup complete. Only one Flow dashboard should remain.")
        except Exception as e:
            print(f"Error during tab cleanup: {e}")

if __name__ == "__main__":
    asyncio.run(clean_tabs_and_focus_flow())
