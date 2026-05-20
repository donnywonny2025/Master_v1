/**
 * MASTER TRANSCRIBER — Meeting Notes Server
 * 
 * Repurposed from The Seeing Eye (interview HUD) into a
 * meeting note-taking tool. Captures system audio via BlackHole,
 * streams to Deepgram for real-time transcription with speaker
 * diarization, and saves timestamped meeting transcripts.
 * 
 * Usage:
 *   npm start
 *   Then open http://localhost:4401 in your browser
 *   Click "Start Recording" before joining a Zoom/call
 * 
 * Prerequisites:
 *   - BlackHole 2ch virtual audio device installed
 *   - Zoom audio output routed through BlackHole (via Multi-Output Device)
 *   - Deepgram API key in .env
 */

import 'dotenv/config';
import express from 'express';
import { createServer } from 'http';
import { Server as SocketIO } from 'socket.io';
import { dirname, join } from 'path';
import { fileURLToPath } from 'url';
import { mkdirSync, appendFileSync, writeFileSync, readdirSync, readFileSync, statSync } from 'fs';
import { Transcriber } from './transcriber.js';

const __dir = dirname(fileURLToPath(import.meta.url));
const PORT = process.env.PORT || 4401;
const TRANSCRIPT_DIR = process.env.TRANSCRIPT_DIR || join(__dir, 'transcripts');

// Ensure transcript directory exists
mkdirSync(TRANSCRIPT_DIR, { recursive: true });

export async function startServer() {
  const app = express();
  const httpServer = createServer(app);
  const io = new SocketIO(httpServer, { cors: { origin: '*' } });

  // Serve the web UI
  app.use(express.static(join(__dir, 'ui')));

  // Health check
  app.get('/health', (req, res) => {
    res.json({
      status: 'ok',
      deepgram: !!process.env.DEEPGRAM_API_KEY,
      model: process.env.DEEPGRAM_MODEL || 'nova-2',
    });
  });

  // ── Transcript History API ────────────────────

  // List all saved transcripts (newest first)
  app.get('/api/transcripts', (req, res) => {
    try {
      const files = readdirSync(TRANSCRIPT_DIR)
        .filter(f => f.endsWith('.md'))
        .map(f => {
          const fp = join(TRANSCRIPT_DIR, f);
          const st = statSync(fp);
          // Parse first few lines for metadata
          const content = readFileSync(fp, 'utf-8');
          const lines = content.split('\n');
          const title = (lines[0] || '').replace(/^#+\s*/, '').replace('Meeting Notes — ', '');
          const date = (lines.find(l => l.startsWith('**Date:**')) || '').replace('**Date:** ', '');
          const duration = (lines.find(l => l.startsWith('**Duration:**')) || '').replace('**Duration:** ', '');
          const segs = (lines.find(l => l.startsWith('**Total segments:**')) || '').replace('**Total segments:** ', '');
          return {
            filename: f,
            title: title || f,
            date,
            duration,
            segments: segs,
            size: st.size,
            mtime: st.mtime,
          };
        })
        .sort((a, b) => new Date(b.mtime) - new Date(a.mtime));
      res.json({ transcripts: files });
    } catch (err) {
      res.json({ transcripts: [] });
    }
  });

  // Get a single transcript's full content
  app.get('/api/transcripts/:filename', (req, res) => {
    const safe = req.params.filename.replace(/[^a-zA-Z0-9._-]/g, '');
    const fp = join(TRANSCRIPT_DIR, safe);
    try {
      const content = readFileSync(fp, 'utf-8');
      res.json({ filename: safe, content });
    } catch (err) {
      res.status(404).json({ error: 'Transcript not found' });
    }
  });

  // ── Socket.IO — One connection per recording session ──

  io.on('connection', (socket) => {
    console.log('[SERVER] Client connected:', socket.id);

    let transcriber = null;
    let sessionFile = null;
    let sessionStart = null;
    let fullTranscript = [];          // Array of { time, speaker, text }
    let currentUtterance = [];        // Buffer for current speaker turn

    // ── Start Recording ─────────────────────────

    socket.on('start-recording', async ({ label }) => {
      if (!process.env.DEEPGRAM_API_KEY) {
        socket.emit('error', { message: 'DEEPGRAM_API_KEY not configured in .env' });
        return;
      }

      sessionStart = new Date();
      const dateStr = sessionStart.toISOString().split('T')[0];
      const timeStr = sessionStart.toTimeString().split(' ')[0].replace(/:/g, '');
      const safeName = (label || 'meeting').replace(/[^a-zA-Z0-9_-]/g, '_').substring(0, 50);
      sessionFile = join(TRANSCRIPT_DIR, `${dateStr}_${timeStr}_${safeName}.md`);

      // Write session header
      const header = [
        `# Meeting Notes — ${label || 'Untitled Meeting'}`,
        `**Date:** ${sessionStart.toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}`,
        `**Started:** ${sessionStart.toLocaleTimeString('en-US')}`,
        `**Model:** ${process.env.DEEPGRAM_MODEL || 'nova-2'}`,
        '',
        '---',
        '',
      ].join('\n');
      writeFileSync(sessionFile, header);

      fullTranscript = [];
      currentUtterance = [];

      // Initialize Deepgram
      transcriber = new Transcriber(process.env.DEEPGRAM_API_KEY, {
        model: process.env.DEEPGRAM_MODEL,
      });

      transcriber.on('transcript-partial', (text, speaker) => {
        socket.emit('transcript-partial', { text, speaker });
      });

      transcriber.on('transcript-final', (text, speaker) => {
        const elapsed = getElapsed(sessionStart);
        const entry = { time: elapsed, speaker, text };
        currentUtterance.push(entry);
        fullTranscript.push(entry);

        socket.emit('transcript-final', { text, speaker, time: elapsed });

        // Append to file immediately (crash-safe)
        const speakerLabel = speaker !== null && speaker !== undefined ? `**Speaker ${speaker + 1}:** ` : '';
        appendFileSync(sessionFile, `\`${elapsed}\` ${speakerLabel}${text}\n\n`);
      });

      transcriber.on('utterance-end', () => {
        // Speaker finished a turn — emit for UI grouping
        if (currentUtterance.length > 0) {
          socket.emit('utterance-complete', {
            segments: currentUtterance,
          });
          currentUtterance = [];
        }
      });

      transcriber.on('error', (err) => {
        socket.emit('error', { message: err.message });
      });

      await transcriber.start();
      socket.emit('recording-started', { file: sessionFile });
      console.log(`[SERVER] Recording started → ${sessionFile}`);
    });

    // ── Receive Audio Data ──────────────────────

    socket.on('audio-data', (data) => {
      if (transcriber) {
        transcriber.sendAudio(Buffer.from(data));
      }
    });

    // ── Stop Recording ──────────────────────────

    socket.on('stop-recording', () => {
      if (transcriber) {
        transcriber.stop();
        transcriber = null;
      }

      // Write session footer
      if (sessionFile && sessionStart) {
        const endTime = new Date();
        const duration = getElapsed(sessionStart, endTime);
        const footer = [
          '',
          '---',
          '',
          `**Ended:** ${endTime.toLocaleTimeString('en-US')}`,
          `**Duration:** ${duration}`,
          `**Total segments:** ${fullTranscript.length}`,
        ].join('\n');
        appendFileSync(sessionFile, footer);
        console.log(`[SERVER] Recording saved → ${sessionFile} (${fullTranscript.length} segments, ${duration})`);
      }

      socket.emit('recording-stopped', {
        file: sessionFile,
        segments: fullTranscript.length,
      });

      sessionFile = null;
      sessionStart = null;
      fullTranscript = [];
      currentUtterance = [];
    });

    // ── Disconnect Cleanup ──────────────────────

    socket.on('disconnect', () => {
      if (transcriber) {
        transcriber.stop();
        transcriber = null;
      }
      console.log('[SERVER] Client disconnected:', socket.id);
    });
  });

  // ── Start ─────────────────────────────────────

  httpServer.listen(PORT, () => {
    console.log(`\n  ╔═══════════════════════════════════════╗`);
    console.log(`  ║   MASTER TRANSCRIBER — Meeting Notes  ║`);
    console.log(`  ╠═══════════════════════════════════════╣`);
    console.log(`  ║  UI:       http://localhost:${PORT}       ║`);
    console.log(`  ║  Deepgram: ${process.env.DEEPGRAM_API_KEY ? '✓ Connected' : '✗ Missing key'}              ║`);
    console.log(`  ║  Model:    ${(process.env.DEEPGRAM_MODEL || 'nova-2').padEnd(24)}║`);
    console.log(`  ║  Output:   ./transcripts/             ║`);
    console.log(`  ╚═══════════════════════════════════════╝\n`);
  });

  return httpServer;
}

// ── Helpers ───────────────────────────────────────

function getElapsed(start, end = new Date()) {
  const diff = Math.floor((end - start) / 1000);
  const h = Math.floor(diff / 3600);
  const m = Math.floor((diff % 3600) / 60);
  const s = diff % 60;
  if (h > 0) return `${h}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
  return `${m}:${String(s).padStart(2, '0')}`;
}

// Run standalone
startServer();
