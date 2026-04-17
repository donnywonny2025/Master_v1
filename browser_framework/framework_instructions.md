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

## 7. The "Human-in-the-Loop" (HITL) Harmonic Protocol / Anti-Bot Evasion
We do not over-engineer python scripts to beat Captchas, complex logins, or annoying cookie popups. The overarching philosophy here is **Anti-Bot Evasion**. High-security platforms (Google, Apple, Banks) easily detect automated CDP clicks/typing. The safest way to bypass bot-detection is to have the human user literally use their own mouse and keyboard. The system works in harmony with the user, who is physically watching the same visual tab.
- **The Subagent Prompt:** When deploying the subagent, you MUST append this instruction: *"If you encounter a Login screen (especially Google/Apple/Banking), a Captcha, or a screen-blocking popup preventing access, DO NOT attempt to type or bypass it yourself. Doing so triggers bot detection. Immediately HALT and return exactly: 'HITL REQUIRED: [Describe the block]'. Let the human handle it."*
- **The Action:** When the subagent halts and flags `HITL REQUIRED`, the Master (me) will simply notify the user (you), wait for you to type in the credentials natively to naturally bypass bot flags, and then resume operations seamlessly.

## 8. Smart Subagent Traversal Protocol (Codified Constraint Rule)
When dispatching the subagent to interact autonomously inside heavy canvas or highly secure platforms (e.g. Google Flow tool dashboards), the Master Assistant MUST inject the following strict constraint block to guarantee stability and prevent bot-flags:
> **CRITICAL 'SMART APPROACH' CONSTRAINTS:**
> 1. Do not trigger bot checks by clicking rapidly or at 0,0. Slow down mouse events if possible.
> 2. If you find that the UI is an HTML5 `<canvas>` and you cannot reliably determine standard DOM coordinates for the hit-target, DO NOT GUESS. Halt instantly and return 'ERROR: CANVAS BLINDNESS'.
> 3. If a security check, waitlist modal, or popup appears, HALT instantly and return 'HITL REQUIRED'.
> 4. Only proceed with clicking if you are 100% physically certain of the DOM node positioning.

## 9. The Sovereign Eyes (External Layer Verification)
The defining characteristic of this architecture is **not** blindly trusting the subagent's internal API telemetry. We do not depend on the browser telling us it worked. The Master Assistant operates as an external, sovereign oversight layer. 
- **The Rule:** Anytime the Master Assistant dispatches the subagent to perform an action, the Master MUST immediately follow up by executing `execution/look.sh`.
- **The Action:** The Master will ingest the resulting physical snapshot of the monitor to visually guarantee reality. If the browser closed, crashed, or hallucinated, the Master sees it explicitly as an external observer.
- **The Result:** The Master reports the actual physical confirmation back to the user to close the communication loop perfectly.

