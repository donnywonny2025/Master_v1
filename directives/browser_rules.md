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

