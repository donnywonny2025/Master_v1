/**
 * MASTER TRANSCRIBER — Meeting Notes Frontend
 * 
 * Captures system audio (via BlackHole virtual device) and
 * streams it to the backend for real-time Deepgram transcription.
 * Displays live transcript with speaker labels and timestamps.
 * Includes session history sidebar for browsing past transcripts.
 */

// ── State ──────────────────────────────────────

let socket = null;
let isRecording = false;
let audioContext = null;
let mediaStream = null;
let processorNode = null;
let timerInterval = null;
let recordStart = null;
let segmentCount = 0;
let viewingHistory = false;  // true when viewing a past transcript

// ── DOM ────────────────────────────────────────

const statusEl = document.getElementById('status');
const timerEl = document.getElementById('timer');
const statusDot = document.getElementById('status-dot');
const logoIcon = document.querySelector('.logo-icon');
const meetingInput = document.getElementById('meeting-label');
const recordBtn = document.getElementById('record-btn');
const btnIcon = document.getElementById('btn-icon');
const btnText = document.getElementById('btn-text');
const transcriptArea = document.getElementById('transcript-area');
const transcriptEmpty = document.getElementById('transcript-empty');
const transcriptLines = document.getElementById('transcript-lines');
const transcriptPartial = document.getElementById('transcript-partial');
const footerModel = document.getElementById('footer-model');
const footerFile = document.getElementById('footer-file');
const footerCount = document.getElementById('footer-count');

// Sidebar
const sidebar = document.getElementById('sidebar');
const sidebarToggle = document.getElementById('sidebar-toggle');
const sessionList = document.getElementById('session-list');
const newSessionBtn = document.getElementById('new-session-btn');

// Viewer
const viewerArea = document.getElementById('viewer-area');
const viewerBack = document.getElementById('viewer-back');
const viewerTitle = document.getElementById('viewer-title');
const viewerContent = document.getElementById('viewer-content');
const controlsEl = document.getElementById('controls');

// ── Initialize ─────────────────────────────────

function init() {
  socket = io();

  socket.on('connect', () => {
    statusDot.classList.add('connected');
    console.log('[UI] Connected to server');
  });

  socket.on('disconnect', () => {
    statusDot.classList.remove('connected');
  });

  // Recording started confirmation
  socket.on('recording-started', ({ file }) => {
    footerFile.textContent = file.split('/').pop();
    console.log('[UI] Recording to:', file);
  });

  // Live partial transcript (green, updating)
  socket.on('transcript-partial', ({ text, speaker }) => {
    transcriptPartial.textContent = text;
    autoScroll();
  });

  // Final transcript segment (committed)
  socket.on('transcript-final', ({ text, speaker, time }) => {
    transcriptPartial.textContent = '';
    addTranscriptLine(time, speaker, text);
    segmentCount++;
    footerCount.textContent = `${segmentCount} segment${segmentCount !== 1 ? 's' : ''}`;
    autoScroll();
  });

  // Recording stopped
  socket.on('recording-stopped', ({ file, segments }) => {
    console.log(`[UI] Session saved: ${file} (${segments} segments)`);
    loadSessionHistory(); // refresh sidebar
  });

  // Errors
  socket.on('error', ({ message }) => {
    console.error('[UI] Error:', message);
    statusEl.textContent = 'Error: ' + message;
  });

  // Button handlers
  recordBtn.addEventListener('click', toggleRecording);
  sidebarToggle.addEventListener('click', toggleSidebar);
  newSessionBtn.addEventListener('click', showRecorder);
  viewerBack.addEventListener('click', showRecorder);

  // Enter key starts recording
  meetingInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !isRecording) toggleRecording();
  });

  // Fetch health to show model info
  fetch('/health')
    .then(r => r.json())
    .then(data => {
      footerModel.textContent = data.model || 'nova-2';
    })
    .catch(() => {});

  // Load session history
  loadSessionHistory();
}

// ── Sidebar ────────────────────────────────────

function toggleSidebar() {
  sidebar.classList.toggle('collapsed');
}

async function loadSessionHistory() {
  try {
    const res = await fetch('/api/transcripts');
    const data = await res.json();
    renderSessionList(data.transcripts || []);
  } catch (err) {
    console.error('[UI] Failed to load history:', err);
  }
}

function renderSessionList(transcripts) {
  if (transcripts.length === 0) {
    sessionList.innerHTML = '<div class="sidebar-empty">No recordings yet</div>';
    return;
  }

  sessionList.innerHTML = transcripts.map(t => {
    const dur = t.duration || '—';
    const segs = t.segments || '0';
    return `
      <div class="session-item" data-filename="${t.filename}" onclick="viewTranscript('${t.filename}')">
        <div class="session-title">${escapeHtml(t.title)}</div>
        <div class="session-meta">
          <span>${dur}</span>
          <span>${segs} seg</span>
        </div>
      </div>
    `;
  }).join('');
}

// ── View Past Transcript ───────────────────────

async function viewTranscript(filename) {
  try {
    const res = await fetch(`/api/transcripts/${encodeURIComponent(filename)}`);
    const data = await res.json();
    if (data.error) {
      console.error('[UI] Transcript not found');
      return;
    }

    viewingHistory = true;

    // Hide recorder, show viewer
    transcriptArea.style.display = 'none';
    controlsEl.style.display = 'none';
    viewerArea.style.display = 'flex';

    // Parse and render the markdown content
    const lines = data.content.split('\n');
    const title = (lines[0] || '').replace(/^#+\s*/, '');
    viewerTitle.textContent = title;

    // Render content
    viewerContent.innerHTML = renderMarkdownTranscript(lines);

    // Highlight active session in sidebar
    document.querySelectorAll('.session-item').forEach(el => {
      el.classList.toggle('active', el.dataset.filename === filename);
    });

    footerFile.textContent = filename;
    footerCount.textContent = 'viewing history';

  } catch (err) {
    console.error('[UI] Failed to load transcript:', err);
  }
}

function renderMarkdownTranscript(lines) {
  let html = '';
  let inMeta = true;
  let metaLines = [];
  let bodyLines = [];
  let footerLines = [];
  let hitFirstSeparator = false;
  let hitSecondSeparator = false;

  for (const line of lines) {
    if (line.startsWith('---')) {
      if (!hitFirstSeparator) {
        hitFirstSeparator = true;
        continue;
      } else {
        hitSecondSeparator = true;
        continue;
      }
    }

    if (!hitFirstSeparator) {
      metaLines.push(line);
    } else if (!hitSecondSeparator) {
      if (line.trim()) bodyLines.push(line);
    } else {
      if (line.trim()) footerLines.push(line);
    }
  }

  // Meta header
  html += '<div class="v-meta">';
  for (const m of metaLines) {
    if (m.startsWith('#')) continue; // skip title (shown in viewer-title)
    if (m.trim()) {
      html += `<div>${m.replace(/\*\*/g, '')}</div>`;
    }
  }
  html += '</div>';

  // Transcript body
  for (const line of bodyLines) {
    // Parse: `0:03` **Speaker 1:** text
    const match = line.match(/^`([^`]+)`\s*(?:\*\*Speaker (\d+):\*\*)?\s*(.*)$/);
    if (match) {
      const [, time, speaker, text] = match;
      const speakerClass = speaker ? `v-speaker-${parseInt(speaker) - 1}` : '';
      const speakerLabel = speaker ? `<span class="v-speaker ${speakerClass}">S${speaker}</span>` : '';
      html += `<div class="v-line"><span class="v-time">${time}</span>${speakerLabel}${escapeHtml(text)}</div>`;
    } else if (line.trim()) {
      html += `<div class="v-line">${escapeHtml(line)}</div>`;
    }
  }

  // Footer
  if (footerLines.length > 0) {
    html += '<div class="v-footer">';
    for (const f of footerLines) {
      html += `<div>${f.replace(/\*\*/g, '')}</div>`;
    }
    html += '</div>';
  }

  return html;
}

function showRecorder() {
  viewingHistory = false;
  transcriptArea.style.display = '';
  controlsEl.style.display = '';
  viewerArea.style.display = 'none';

  // Clear active highlights
  document.querySelectorAll('.session-item').forEach(el => {
    el.classList.remove('active');
  });

  footerFile.textContent = isRecording ? footerFile.textContent : 'No active session';
  footerCount.textContent = `${segmentCount} segment${segmentCount !== 1 ? 's' : ''}`;
}

// ── Toggle Recording ───────────────────────────

async function toggleRecording() {
  if (viewingHistory) {
    showRecorder();
    return;
  }

  if (isRecording) {
    // Stop
    isRecording = false;
    socket.emit('stop-recording');
    stopAudioCapture();
    stopTimer();

    recordBtn.classList.remove('recording');
    statusEl.classList.remove('recording');
    statusDot.classList.remove('recording');
    logoIcon.classList.remove('recording');
    timerEl.classList.remove('recording');
    btnText.textContent = 'Start Recording';
    statusEl.textContent = 'Saved';
    meetingInput.disabled = false;
  } else {
    // Start
    const label = meetingInput.value.trim() || 'Meeting';
    isRecording = true;
    segmentCount = 0;
    transcriptLines.innerHTML = '';
    transcriptPartial.textContent = '';
    transcriptEmpty.style.display = 'none';
    footerCount.textContent = '0 segments';

    await startAudioCapture();
    socket.emit('start-recording', { label });
    startTimer();

    recordBtn.classList.add('recording');
    statusEl.classList.add('recording');
    statusDot.classList.add('recording');
    logoIcon.classList.add('recording');
    timerEl.classList.add('recording');
    btnText.textContent = 'Stop Recording';
    btnIcon.textContent = '■';
    statusEl.textContent = 'Recording';
    meetingInput.disabled = true;
  }
}

// ── Audio Capture ──────────────────────────────

async function startAudioCapture() {
  try {
    const devices = await navigator.mediaDevices.enumerateDevices();
    const audioInputs = devices.filter(d => d.kind === 'audioinput');

    // Look for BlackHole virtual audio device
    const blackhole = audioInputs.find(d => d.label.toLowerCase().includes('blackhole'));

    const constraints = {
      channelCount: 1,
      sampleRate: 16000,
      echoCancellation: false,
      noiseSuppression: false,
      autoGainControl: false,
    };

    if (blackhole) {
      constraints.deviceId = { exact: blackhole.deviceId };
      console.log('[UI] Audio source: BlackHole 2ch');
    } else {
      console.warn('[UI] BlackHole not found — using default mic');
      console.warn('[UI] Install BlackHole to capture Zoom/system audio');
    }

    mediaStream = await navigator.mediaDevices.getUserMedia({ audio: constraints });
    audioContext = new AudioContext({ sampleRate: 16000 });
    const source = audioContext.createMediaStreamSource(mediaStream);

    // ScriptProcessor to convert float32 → int16 PCM
    processorNode = audioContext.createScriptProcessor(4096, 1, 1);
    processorNode.onaudioprocess = (event) => {
      if (!isRecording) return;
      const inputData = event.inputBuffer.getChannelData(0);
      const pcmBuffer = new Int16Array(inputData.length);
      for (let i = 0; i < inputData.length; i++) {
        const s = Math.max(-1, Math.min(1, inputData[i]));
        pcmBuffer[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
      }
      socket.emit('audio-data', pcmBuffer.buffer);
    };

    source.connect(processorNode);
    processorNode.connect(audioContext.destination);
    console.log('[UI] Audio capture started');
  } catch (err) {
    console.error('[UI] Audio capture failed:', err.message);
    statusEl.textContent = 'Mic error — check permissions';
  }
}

function stopAudioCapture() {
  if (processorNode) { processorNode.disconnect(); processorNode = null; }
  if (mediaStream) { mediaStream.getTracks().forEach(t => t.stop()); mediaStream = null; }
  if (audioContext) { audioContext.close(); audioContext = null; }
  console.log('[UI] Audio capture stopped');
}

// ── Transcript Rendering ───────────────────────

function addTranscriptLine(time, speaker, text) {
  const line = document.createElement('div');
  line.className = 'transcript-line';

  const timeSpan = document.createElement('span');
  timeSpan.className = 'transcript-time';
  timeSpan.textContent = time || '';

  const speakerSpan = document.createElement('span');
  const speakerNum = speaker !== null && speaker !== undefined ? speaker : '?';
  speakerSpan.className = `transcript-speaker speaker-${speakerNum}`;
  speakerSpan.textContent = speakerNum !== '?' ? `S${speakerNum + 1}` : '';

  const textSpan = document.createElement('span');
  textSpan.className = 'transcript-text';
  textSpan.textContent = text;

  line.appendChild(timeSpan);
  line.appendChild(speakerSpan);
  line.appendChild(textSpan);
  transcriptLines.appendChild(line);
}

function autoScroll() {
  transcriptArea.scrollTop = transcriptArea.scrollHeight;
}

// ── Timer ──────────────────────────────────────

function startTimer() {
  recordStart = Date.now();
  timerInterval = setInterval(updateTimer, 1000);
}

function stopTimer() {
  clearInterval(timerInterval);
  timerInterval = null;
}

function updateTimer() {
  if (!recordStart) return;
  const diff = Math.floor((Date.now() - recordStart) / 1000);
  const m = Math.floor(diff / 60);
  const s = diff % 60;
  const h = Math.floor(m / 60);
  if (h > 0) {
    timerEl.textContent = `${h}:${String(m % 60).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
  } else {
    timerEl.textContent = `${m}:${String(s).padStart(2, '0')}`;
  }
}

// ── Helpers ────────────────────────────────────

function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

// ── Boot ───────────────────────────────────────

init();
