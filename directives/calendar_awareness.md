# Calendar Awareness Protocol

> **Trigger:** Any time the user mentions an appointment, meeting, schedule, "who am I seeing," "give me the number," or any time/date-related request about their day.

---

## Mandatory Lookup Chain

When the user asks about appointments, contacts, or their schedule — **DO NOT ASK THEM TO EXPLAIN.** Run this chain automatically:

### Step 1: Check the Contacts KI
- **File:** `knowledge/Contacts_And_Calendar/artifacts/Master_Reference.md`
- Contains all verified contacts, phone numbers, Zoom links, and recurring appointments
- This is your FIRST stop for any "give me the number" request

### Step 2: Check the Dashboard "Today's Focus"
- **Source:** The SYSTEM dashboard at `localhost:3111` pulls today's events from Apple Calendar via WebSocket
- **Data flow:** `server.js` → WebSocket `calendar` event → `feeds.js:autoFocusFromCalendar()` → renders in the "Today's Focus" panel
- **The dashboard knows today's schedule.** If you need to see what's on today, scrape `localhost:3111` or check the server's calendar endpoint

### Step 3: Check Calendar Files
- **Directory:** `/Volumes/WORK 2TB/WORK 2026/MASTER V1/legal/calendar/`
- Contains manually created event files with full details (Zoom links, passcodes, prep checklists)

### Step 4: Check the Focus Redesign Plan (Legacy)
- **File:** Focus redesign plan artifact in the conversation brain
- Contains contact enrichment data (phone, address, org) for dashboard event cards
- **Contacts stored here:** Dr. Almaaitah, CallieBea Bowers, Dermatologist (pending)

---

## Rules

1. **NEVER ask "who is your doctor?"** if the user says "my rheumatologist" or "my appointment today" — look it up.
2. **NEVER say "I don't have that"** before exhausting ALL four steps above.
3. **Phone numbers are urgent.** When the user asks for a number, give it IMMEDIATELY — don't bury it in paragraphs of context. Number first, details second.
4. **Update the KI** any time you discover a new contact or appointment detail. The Contacts KI must be the single source of truth.
5. **The dashboard is ground truth for today's schedule.** It pulls from Apple Calendar in real-time. If unsure what's on today, check the dashboard.

---

## Known Contacts (Quick Reference)

| Who | Phone | Where |
|-----|-------|-------|
| Dr. Saja M. Almaaitah (Rheumatologist) | (616) 267-7293 | Corewell Health, Grand Rapids MI |
| CallieBea Bowers (Probation) | (269) 673-0360 | Allegan County Probation |
| Dare'l McMillian | (248) 778-6468 | M2 McMillian Media |
| El Centro Justice Court | (602) 372-6300 | Maricopa County |

*Full details in the Contacts KI: `knowledge/Contacts_And_Calendar/artifacts/Master_Reference.md`*
