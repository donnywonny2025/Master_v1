# Execution & State Alignment Protocol

## Verify State Alignment Before Claiming Success

**Never assume an execution succeeded solely because the code was updated or a localized terminal command exited with code 0.** You are operating within an interconnected local environment where overlapping processes, stubborn ports, and browser-layer caches frequently cause the *User's visible state* to diverge from your *Engine's mapped state*.

To maintain structural integrity, you must enforce the following alignment checks whenever pushing live updates:

1. **Aggressive Process Disconnection:** When replacing a running server or background pipeline (e.g. Tornado, WebSockets, Python endpoints), gracefully terminating a child process is insufficient if the primary loop maintains a death-grip on the port. You must mathematically verify the port is free using `lsof` tracking and execute a precision `SIGKILL` on any rogue zombie PID blocking your deployment before launching the new version.

2. **Cache-Busting Reload Sequences:** Updating the physical HTML/CSS file on the hard disk does nothing if the User's Chrome instance serves a cached string from memory. Whenever deploying visual/frontend alterations that the user needs to evaluate, you must deploy a headless CDP (Chrome DevTools Protocol) script to force a deep `Page.reload(ignoreCache=True)` onto their active browser tab natively. 

3. **No Assumptions:** Never tell the user "The layout is updated, refresh and tell me what you see!" You must execute the deployment code, run the regex process-sweep to ensure the new application logic is actively bound to the port, trigger the cache-clearing browser injection, and *only then* declare success. 

What the User physically sees MUST be forced into exact deterministic synchronization with what your internal model assumes you just built.

4. **Strict Single-Tab Adherence:** Native application spawns cause un-curated tab stacking which clutters the User's display. You must algorithmically enforce a zero-duplication workspace. If running the internal Chromium wrapper natively, utilize `.tmp/close_tabs_cdp.py` to strip the DevTools nodes. If operating within the physical macOS Google Chrome application, you must utilize an AppleScript injection array (`.tmp/close_chrome_tabs_applescript.py`) to systematically hunt and slice away overlapping physical browser tabs until mathematically only one isolated execution tab remains active.
