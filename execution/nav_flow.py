import asyncio
from playwright.async_api import async_playwright

async def navigate_to_flow():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://localhost:9222")
        
        target_page = None
        for context in browser.contexts:
            for page in context.pages:
                if page.url.startswith("about:blank") or "google.com" in page.url or "labs.google" in page.url:
                    target_page = page
                    break
            if target_page:
                break
                
        if not target_page:
            print("No active tab found.")
            return

        print("Navigating to Google Flow...")
        await target_page.goto("https://labs.google/fx/tools/flow", timeout=60000)
        await asyncio.sleep(2)  # Allow JS to settle
        print("Navigation Complete.")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(navigate_to_flow())
