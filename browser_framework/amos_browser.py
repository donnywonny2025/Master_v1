#!/usr/bin/env python3
"""
Universal AMOS Browser Framework
A hardened, persistent Playwright environment for agentic systems.

Features:
- Single Window, Persistent Cookies/Sessions
- Exposes CDP port 9222 for external tab cleanup/sweeping
- Self-healing PID locks
"""

import asyncio
import os
import signal
import sys
import json
from pathlib import Path
from playwright.async_api import async_playwright

# Use the current working directory where the agent runs it, ensuring portability across projects.
BASE = os.getcwd()
PROFILE_DIR = os.path.expanduser("~/.gemini/antigravity-browser-profile")
PID_FILE = os.path.join(BASE, ".tmp", "amos_browser.pid")

# ── PID Lock ────────────────────────────────────────────────────────
def check_pid_lock():
    if os.path.exists(PID_FILE):
        with open(PID_FILE) as f:
            old_pid_text = f.read().strip()
            if not old_pid_text.isdigit():
                return
            old_pid = int(old_pid_text)
        try:
            os.kill(old_pid, 0)
            print(f"[AMOS] Already running (PID {old_pid}). Exiting.")
            sys.exit(0)
        except OSError:
            pass  

def write_pid():
    os.makedirs(os.path.dirname(PID_FILE), exist_ok=True)
    with open(PID_FILE, "w") as f:
        f.write(str(os.getpid()))

def clear_pid():
    if os.path.exists(PID_FILE):
        os.remove(PID_FILE)

# ── Main ────────────────────────────────────────────────────────────
async def main():
    check_pid_lock()
    write_pid()

    print(f"[AMOS] Starting Universal persistent browser (PID {os.getpid()})")
    print(f"[AMOS] Profile running in: {PROFILE_DIR}")
    print("[AMOS] Exposing CDP on localhost:9222 for Tab Sweeping.")

    async with async_playwright() as pw:
        context = await pw.chromium.launch_persistent_context(
            user_data_dir=PROFILE_DIR,
            headless=False,
            no_viewport=True,          
            channel="chrome",          
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--no-first-run",
                "--no-default-browser-check",
                "--remote-debugging-port=9222",
                "--window-position=0,0",          # Lock to top-left of the Acer monitor
                "--window-size=986,1050"          # Precisely sized for a 986x963 viewport + UI tabs
            ],
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
            ignore_default_args=["--enable-automation"],
        )

        await context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => false});")

        # Collapse to one tab on startup
        while len(context.pages) > 1:
            await context.pages[-1].close()

        page = context.pages[0] if context.pages else await context.new_page()
        
        # Keep process alive silently
        try:
            while True:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            pass
        finally:
            print("\n[AMOS] Shutting down...")
            await context.close()
            clear_pid()
            print("[AMOS] Clean exit.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        clear_pid()
        print("\n[AMOS] Interrupted. PID lock cleared.")
