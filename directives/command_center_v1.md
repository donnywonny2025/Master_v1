# Command Center V1 — Hermes Dashboard (Archived)

## Overview
A homegrown Tornado-based web dashboard that embeds a Hermes CLI terminal via `terminado` alongside a real-time system activity feed.

## Architecture
- **File**: `execution/dashboard.py` (329 lines)
- **Port**: 9120
- **Components**:
  - `DashboardPageHandler` — Serves inline HTML with xterm.js terminal
  - `EventHandler` — WebSocket at `/events` for real-time activity feed
  - `EventBroker` — Thread-safe broadcast to all connected WebSocket clients
  - `WorkspaceChangeHandler` — Watchdog file system monitor (ignores .git, .tmp, node_modules)
  - `tail_agent_log()` — Tails `.agent_activity.log` for agent events
  - `terminado.SingleTermManager` — Bridges PTY running `hermes chat` to browser WebSocket at `/terminal`

## How to Launch
```bash
cd "/Volumes/WORK 2TB/WORK 2026/MASTER V1"
source execution/hermes-agent/.venv/bin/activate  # Must use web-env or .venv with tornado+terminado
python execution/dashboard.py
# Opens at http://127.0.0.1:9120
```

## Supporting Scripts
- `execution/direct_inject.py` — WebSocket injection to type commands into the terminal remotely
- `execution/web_terminal.py` — Earlier standalone terminal wrapper (superseded by dashboard.py)

## Design
- Dark theme, Inter font, glassmorphism panels
- Top panel (flex 5): Interactive Shell (xterm.js)
- Bottom panel (flex 3): System Activity Feed with animated slide-in entries
- Green "Live" status indicator in header

## Why Archived
Replaced by `hermes-webui` (https://github.com/nesquena/hermes-webui) which provides a production-grade three-panel UI with session management, cron job controls, skills, memory, workspace browser, and mobile support.
