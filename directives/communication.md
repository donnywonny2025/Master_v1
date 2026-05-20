# Communication Directive

## Session Summaries

At the end of every response, provide a brief **"Summary"** section that recaps what was just accomplished. This should be:

- **Concise** — bullet points, not paragraphs
- **Action-oriented** — what was done, not what was discussed
- **Cumulative when appropriate** — if multiple things happened, list them all
- **Honest** — if something is pending or blocked, say so

### Format

```
---
**Summary:**
- ✅ Thing that was completed
- ✅ Another thing done
- ⏳ Thing still waiting on user input
- 🔜 Next step when ready
```

## Subagent / Browser Visuals

**NEVER** embed screenshots, `.webp` recordings, or images of the browser subagent in the chat interface. 

The user has a split-screen setup and can physically see the browser operating on the left half of the monitor. Embedding recordings clutters the chat and is completely unnecessary. Execute the browser commands silently and just report what was found or completed.

---

## Contact Data Verification

**NEVER present unverified contact information (phone numbers, addresses, extensions) as fact.** Every contact data point stored in the system must be tagged with its verification status:

### Verification Tiers

| Tier | Label | Meaning |
|------|-------|---------|
| ✅ | **Verified** | Confirmed from an authoritative source (official website, direct correspondence, user-provided) |
| ⚠️ | **Unverified** | Scraped, inferred, or entered without cross-referencing — MUST be flagged as such when presented to the user |
| ❌ | **Wrong** | Previously entered and confirmed incorrect — update immediately, log the correction |

### Rules

1. **Before presenting any phone number or address to the user**, confirm its source. If the source is your own previous entry, say so.
2. **When entering new contact data**, add a verification comment in the code noting the source.
3. **When a number is found to be wrong**, correct it immediately in all locations (contacts.js, MEMORY.md, any lookup tables).
4. **Never fabricate extensions or direct lines.** If you don't have a verified direct number, say "department main line" and be clear about it.
5. **Cross-reference**: When possible, verify numbers against the official county/org website before storing.
