import asyncio
import sys
import argparse
from playwright.async_api import async_playwright

async def sync_and_sweep(sweep=False):
    async with async_playwright() as p:
        try:
            # Connect to Universal AMOS browser over CDP
            browser = await p.chromium.connect_over_cdp("http://localhost:9222")
            
            # Identify active pages across contexts
            all_pages = []
            for context in browser.contexts:
                all_pages.extend(context.pages)
            
            if not all_pages:
                print("No active pages found. Browser might be ghosted.")
                await browser.close()
                return

            print(f"Found {len(all_pages)} active tabs.")
            
            if sweep:
                # Keep only the very last (most recently focused) tab, kill the rest
                target_page = all_pages[-1]
                killed_count = 0
                for page in all_pages[:-1]:
                    await page.close()
                    killed_count += 1
                print(f"Swept {killed_count} ghost/garbage tabs. Active Tab is now: {target_page.url}")
            else:
                for i, page in enumerate(all_pages):
                    print(f"Tab {i}: {page.url}")
                    
            await browser.close()

        except Exception as e:
            print(f"FATAL: Could not connect to CDP on 9222 (Connection Loss): {e}")
            sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Universal Browser Sync & Sweep Tool")
    parser.add_argument("--sweep", action="store_true", help="Close all tabs except the primary active tab.")
    args = parser.parse_args()
    
    asyncio.run(sync_and_sweep(sweep=args.sweep))
