# Continuous Visual State Verification

**Goal:** Establish an unbreakable, persistent memory of what the user is physically looking at on their screen. The agent must never lose sync with the user's visual reality.

## 1. The Internal Synchronization Loop
At the very beginning of **every single turn** or before initiating any major action:
1. Ask the internal question: *"What is the user currently looking at?"*
2. Cross-reference your mental model (the last thing you put on the screen) with the `Browser State` and `Other open documents` provided in the turn's `ADDITIONAL_METADATA`.
3. If your expectation matches the metadata exactly, state is TRUE.
4. If your expectation does NOT match the metadata, or the user states something looks wrong, state is FALSE.

## 2. The Ground Truth Hammer (`look.sh`)
If state is FALSE (a mismatch occurs), or if you perform *any* visual operation, you **MUST** immediately trigger a physical validation before proceeding. Do not guess. Do not assume.

**Trigger Command:**
```bash
cd "/Volumes/WORK 2TB/WORK 2026/MASTER V1" && bash execution/look.sh "State mismatch / Validation"
```
**View File:**
Immediately use your `view_file` tool to inspect the screenshot produced by the script. Update your mental model and persistent memory to match the exact pixel reality captured in the image.

## 3. The Ledger of Visual Memory
You are bound to essentially maintain a continuous, running internal ledger of the screen. 
- When you open the Command Center dashboard, assert that the user sees it.
- When an operation runs, assert it is visible in the pane.
- Never suggest "you should see X" unless you have already verified via metadata or `look.sh` that X is physically rendered on their screen.

*This directive establishes absolute visual empathy. You and the user look at the same screen, at the same time, always.*
