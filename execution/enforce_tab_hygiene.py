import asyncio
from playwright.async_api import async_playwright

async def enforce_tab_hygiene():
    async with async_playwright() as p:
        try:
            print("Connecting to AMOS Browser CDP...")
            browser = await p.chromium.connect_over_cdp("http://localhost:9222")
            
            kept_one_tab = False
            
            for context in browser.contexts:
                # We iterate over a copy of the pages list since we are closing them dynamically
                pages = list(context.pages)
                for page in pages:
                    url = page.url.lower()
                    # Properly await the title since page.title() is async in python Playwright
                    title = await page.title()
                    
                    if not kept_one_tab and ("flow" in url or "labs.google" in url):
                        kept_one_tab = True
                        print(f"[HYGIENE] Securing Primary Hub: {title} ({url})")
                        await page.bring_to_front()
                    else:
                        print(f"[KILL] Terminating errant tab: {title} ({url})")
                        await page.close()

            print("\n[HYGIENE COMPLETE] Browser environment is sanitized to a single viewport.")
        except Exception as e:
            print(f"Error during tab hygiene sweep: {e}")

if __name__ == "__main__":
    asyncio.run(enforce_tab_hygiene())
