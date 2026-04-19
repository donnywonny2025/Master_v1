# Subagent Tab Management Protocol

This directive enforces how we use the `browser_subagent` tool natively within the Antigravity framework. To keep it fast and prevent chaotic tab sprawl, we bypass heavy external tools. The tab manager is simply strict enforcement of Antigravity's existing metadata context.

## 1. Context Check (The Master Layer)
Before dispatching any subagent, the Master Assistant (me) MUST read the **Browser State** in the `ADDITIONAL_METADATA`.

- **Check 1:** Is the target URL already open?
- **Check 2:** What is the active `Page ID`?

## 2. Dispatching the Subagent (The Scout Layer)
When drafting the `Task` prompt for the `browser_subagent`, the Master Assistant MUST enforce the following rules directly inside the prompt so the subagent acts properly:

- **If the URL is already open:** 
  > *"The page is already open on Page ID [INSERT ID]. Do NOT navigate or open a new tab. Interact with the active UI immediately."*
- **If the URL is NOT open:**
  > *"Navigate to [URL] using the existing active tab: Page ID [INSERT ID]. DO NOT open a new tab. Replace the current active tab."*

## 3. The Prime Directive
- The subagent is NEVER allowed to open `_blank` or new tabs.
- If the subagent fails or reports a crash, it is instantly terminated and the Master layer analyzes the metadata before retrying.

## 4. The Single Visual Strategy
- Maintaining sync between the Assistant and the screen is vital. The user should almost always have **exactly one** relevant tab open as a visual anchor.
## 5. Anti-Hallucination Protocol (The 0x0 Bug)
One of the most dangerous subagent behaviors is when the browser breaks (e.g., renders at `0x0` or goes completely blank), but the subagent hallucinates content and keeps clicking wildly based on bad screenshots.
- **The Check:** The Master Assistant MUST verify the viewport dimensions in the `ADDITIONAL_METADATA` before dispatching. (e.g., `Viewport: 961x963`). If it says `0x0`, DO NOT DISPATCH.
- **The Subagent Prompt:** The prompt MUST include this kill-switch: *"If your initial screenshot is entirely blank, white, or contains zero interactive elements, HALT IMMEDIATELY. Do not guess. Do not click. Return exactly: 'FATAL: BLANK RENDER' so the Master can reset."*

## 6. Connection Loss & Recovery
If the subagent loses CDP connection to the browser:
- It is forbidden from attempting to 'hack' its way back in. It must fail instantly and report the dropped connection.
- The Master Assistant will take over and execute a deterministic Python script to restart or re-attach the persistent Playwright engine (`amos_browser.py`) to refresh the connection pipes before trying again.

## 7. Visual Ground Truth Protocol (`look.sh`)

The `look.sh` command captures the main monitor and logs it to the vision ledger. This is the ONLY way to verify what the user actually sees.

### When to Look
- **Before any browser or workspace change:** Run `look.sh` to establish baseline state.
- **After any browser or workspace change:** Run `look.sh` to verify the result.
- **When the user reports something looks wrong:** Run `look.sh` immediately — don't guess.
- **After tab cleanup operations:** Always confirm the tab count visually.

### How to Use
```bash
cd "/Volumes/WORK 2TB/WORK 2026/MASTER V1"
bash execution/look.sh "Context description of what you're checking"
```

Then `view_file` the resulting screenshot to analyze it. The script logs to `.tmp/screenshots/` and the vision ledger (SQLite).

### What to Check in Every Screenshot
1. **Tab count** — Must be exactly 1 (the Hermes Web Terminal)
2. **Terminal state** — Is Hermes responsive? Is the status bar visible?
3. **Model indicator** — Confirm the correct model is shown in the status bar
4. **IDE state** — Right panel context (Antigravity) should be clean

### Codified Rule
> Do NOT tell the user "it should be fine" or "I believe it worked." **Look first, then report what you actually see.** Screenshots are ground truth. Metadata can lie. The look command doesn't.

## 8. Tab Creation Prevention

The single-tab rule is non-negotiable. These are the codified constraints:

### Never Do This
- `open -a "Google Chrome" [URL]` when a tab already exists — this creates duplicates
- Dispatch a browser subagent with navigation instructions when the page is already open

### Always Do This
- Use WebSocket injection (`direct_inject.py`) to send commands to Hermes — no browser interaction needed
- Use `look.sh` to verify tab count instead of trusting `osascript` tab counters
- If tabs need closing, use keyboard simulation via System Events (`Cmd+W`) — it's the only method proven to work reliably across Chrome profiles

### Recovery Flow
If `look.sh` reveals multiple tabs:
1. Count the tabs visually from the screenshot
2. Use `osascript` with System Events keyboard simulation to close extras
3. Run `look.sh` again to confirm single tab
4. Only proceed once visual confirmation shows exactly 1 tab

## 9. The Split-Brain Profile Defense

Chrome on MacOS operates with multiple user profiles, creating a dangerous "split-brain" failure point if automation targets the wrong one.

- **The Personal Profile:** If launched manually by the user or through basic MacOS commands (e.g., `open -a "Google Chrome" [URL]`), Chrome renders under the default profile WITHOUT the `9222` debugging port. 
- **The Agent Profile:** A secondary, entirely isolated Chromium session launched with `--remote-debugging-port=9222`. 

### The Ultimate Codified Rule for Guaranteed Control:
**Never, ever use native OS commands (like `open -a`) to launch Chrome tabs that need to be controlled or closed later.** 
1. The `browser_subagent` and native CDP scripts (`close_tabs_cdp.py`) **can only see and kill tabs running in the Agent Profile.** They are physically blind to the Personal Profile.
2. If forced to launch a visual interface (like a Web Terminal), it **MUST** be routed natively through the Agent Profile via the `browser_subagent` (or by explicitly launching the Chrome binary passing the `--remote-debugging-port=9222` flag).
3. Attempting to use MacOS AppleScript to close a window launched by `open` will fail unpredictably (`Can't get window 1`) because the OS Apple Events broadcast to the wrong Chrome bundle ID depending on which instance booted first. 
4. If a tab gets orphaned in the Personal Profile, automation is explicitly forbidden from wrestling with MacOS GUI scripts to kill it. Ask the user to close it manually and update the process.
