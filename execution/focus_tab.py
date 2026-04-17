import asyncio
from playwright.async_api import async_playwright

async def focus_signin_tab():
    async with async_playwright() as p:
        try:
            browser = await p.chromium.connect_over_cdp("http://localhost:9222")
            target_page = None
            
            for context in browser.contexts:
                for page in context.pages:
                    if "google.com" in page.url or "google.com/signin" in page.url:
                        target_page = page
                        break
                if target_page:
                    break
                    
            if not target_page:
                print("Could not find the Sign in tab.")
                return

            print("Found Sign in tab. Bringing to foreground...")
            await target_page.bring_to_front()
            await asyncio.sleep(1)
            print("Tab is now active.")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(focus_signin_tab())
