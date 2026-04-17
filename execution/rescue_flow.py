import asyncio
from playwright.async_api import async_playwright

async def rescue_flow():
    async with async_playwright() as p:
        try:
            print("Connecting to AMOS Browser to rescue the dashboard...")
            browser = await p.chromium.connect_over_cdp("http://localhost:9222")
            
            # Grab the only remaining tab
            target_page = browser.contexts[0].pages[0]
            
            print("Redirecting the last remaining tab directly back to Flow Dashboard...")
            await target_page.goto("https://labs.google/fx/tools/flow", timeout=60000)
            await asyncio.sleep(2)
            print("Dashboard restored.")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(rescue_flow())
