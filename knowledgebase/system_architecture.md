# Master V1 System Architecture & Framework Specs

This is the definitive architectural directive for the **Master V1** media production and automation framework. All agents acting within this repository must adhere to these boundaries to maintain system stability and state hygiene.

## 1. Directory Structure & Rules

- **`DOWNLOADS/`**: The explicit local destination for all raw media generation and transcription.
  - **Rule:** Never save files to the root directory or Desktop.
  - **Rule:** Downloaded files natively adopt the `DOWNLOAD_V[X]_[Timestamp]_[Title]` naming convention.
  - **Rule:** JSON Transcripts adopt the identical root suffix (`_Transcript.json`) to guarantee intrinsic linkage on disk.
  
- **`execution/`**: The deterministic "Doing the Work" logic silo.
  - Contains reliable Python scripts that securely handle API calls, data manipulation, and mathematically complex integrations (e.g., FFT sync logic, Whisper processing).
  - All automated actions pass through these scripts; LLMs route parameters to these scripts rather than writing extemporaneous logic during runtime.

- **`execution/bin/`**: The Standalone Binary sandbox.
  - **Rule:** Do NOT rely on global macOS `$PATH`, Homebrew, or user-level installations for heavy dependencies.
  - Contains locally walled-off versions of `yt-dlp` and `ffmpeg` to guarantee 100% portability.
  
- **`knowledgebase/`**: Holds internal persistence tracking (`active_state.md`) and sqlite Vision Ledgers.

## 2. Core Execution Modules

### Browser Hygiene Stack
No longer utilizes AppleScript or Playwright's native context instantiation (which generates extreme tab-bloat).
- **CDP Sweeper (`raw_tab_sweep.py`)**: Directly bridges `localhost:9222` to silently annihilate duplicate tabs, empty profiles, and redundant memory leaks without OS-level permission popups.

### Media Acquisition
- **`youtube_downloader.py`**: A python wrapper dynamically executing the local `bin/yt-dlp` binary. Forces the explicit naming conventions and explicitly routes data down to `DOWNLOADS/`.

### High-Fidelity Audio / Transcription Environment
- **`auto_sync.py`:** A sub-millisecond multicam alignment mathematics engine relying on Fast Fourier Transform (FFT) cross-correlation.
- **`master_transcribo.py`:** PyTorch `CrisperWhisper` offline transformer. 
  - **Logic Patch v1.1:** Wrapped with a robust array analysis block (`try/except IndexError`) rendering it immune to HuggingFace sequence crashing when parsing completely pure audio silence.
  - Leverages local `bin/ffmpeg` flawlessly if the input media container is non-standard (like .m4a fragmented MP4s) bypassing torchaudio.load fails.
- **`xml_autocut_editor.py`:** Absorbs word-level timestamp offsets to emit a perfectly tracked `AutoCut_Timeline.xml` for Premiere Pro.

## 3. Maintenance Protocols

If a specific script routinely encounters an OS-level environment or indexing failure:
1. Wrap logic loops robustly. 
2. Test changes strictly in offline mode before running background daemon batches.
3. Formally update this Architecture document mapping the precise point of failure and resolution mechanism.
4. Execute `chmod +x` against script wrappers when finalizing structural edits.
