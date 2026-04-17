# Persistent Memory Protocol

This directive enforces how the Master Assistant maintains its own memory, ensuring the system never forgets context and the user never has to manually write notes.

## 1. The Startup Hook (Read RAM)
The Master Assistant MUST read `knowledgebase/active_state.md` silently when starting a new session or returning to an old one. This provides instant situational awareness.

## 2. The Auto-Update Protocol (Write RAM)
The Master Assistant is strictly responsible for updating the memory. 
- When a new goal is set, or a background job shifts status, the Master MUST immediately use the `multi_replace_file_content` tool to edit `knowledgebase/active_state.md` in the background. 
- The user should NEVER be asked to manually type out what just happened.

## 3. The Ledger Shift
When a task is officially **completed** (e.g., booking flights, finishing a video export script):
- The Master Assistant MUST append a single sentence summarizing the win to `knowledgebase/memory_ledger.md`.
- The Master Assistant MUST delete the task from the active priorities list in `active_state.md`.
