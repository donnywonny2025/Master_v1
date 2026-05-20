# Master Transcriber — Meeting Notes

Real-time meeting transcription powered by Deepgram Nova-2. Captures system audio and produces timestamped, speaker-labeled Markdown transcripts.

## Quick Start

```bash
cd execution/transcriber
npm start
```

Then open **http://localhost:4401** in your browser.

## Prerequisites

1. **BlackHole 2ch** — Virtual audio device for capturing system audio
   - Install: `brew install blackhole-2ch`
   - Or download from: https://existential.audio/blackhole/

2. **Multi-Output Device** — Route Zoom audio to both speakers AND BlackHole
   - Open **Audio MIDI Setup** (⌘+Space → "Audio MIDI Setup")
   - Click **+** → Create Multi-Output Device
   - Check both your speakers/headphones AND BlackHole 2ch
   - In Zoom: Set speaker output to the Multi-Output Device

3. **Deepgram API Key** — Already configured in `.env` ($200 free credit)

## How It Works

1. Name your meeting in the input field
2. Click **Start Recording** before joining the Zoom/call
3. Audio streams through BlackHole → Deepgram → Live transcript
4. Speaker diarization labels who said what (S1, S2, etc.)
5. Click **Stop Recording** when done
6. Transcript saved to `./transcripts/` as a Markdown file

## Output

Transcripts are saved as Markdown files in `./transcripts/`:

```
transcripts/
  2026-05-20_100000_CallieBea_Probation_Zoom.md
  2026-05-20_140000_Team_Standup.md
```

Each file contains timestamped, speaker-labeled text:

```markdown
# Meeting Notes — CallieBea Probation Zoom
**Date:** Tuesday, May 20, 2026
**Started:** 10:00:00 AM

---

`0:00` **Speaker 1:** Good morning, how are you doing today?
`0:04` **Speaker 2:** I'm doing well, thank you.
```

## Tech Stack

- **Deepgram Nova-2** — Streaming speech-to-text (~300ms latency)
- **Socket.IO** — Real-time audio streaming
- **Express** — Static file serving + health endpoint
- **BlackHole 2ch** — Virtual audio loopback

## Ported From

Originally built as **The Seeing Eye** (interview HUD with real-time LLM answers). Stripped down to focus purely on meeting note-taking and transcript capture.
