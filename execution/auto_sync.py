#!/usr/bin/env python3
"""
FFT-based audio cross-correlation for precise sync offsets.
Uses numpy for instant results instead of slow sample-by-sample.
Generalized for MASTER V1 Framework.
"""
import subprocess, numpy as np, os, argparse

def extract_audio_np(path, start_sec, dur_sec):
    """Extract audio as numpy array via ffmpeg."""
    tmp = "/tmp/_xcorr_master_tmp.raw"
    subprocess.run([
        "ffmpeg", "-y", "-ss", str(start_sec), "-i", path,
        "-t", str(dur_sec), "-vn", "-ac", "1", "-ar", "16000",
        "-f", "s16le", tmp
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    data = np.fromfile(tmp, dtype=np.int16).astype(np.float32) / 32768.0
    os.remove(tmp)
    return data

def find_offset(reference, target):
    """FFT cross-correlation. Returns lag in samples."""
    n = len(reference) + len(target) - 1
    fft_size = 1
    while fft_size < n:
        fft_size *= 2
    
    ref_fft = np.fft.rfft(reference, fft_size)
    tgt_fft = np.fft.rfft(target, fft_size)
    
    # Cross-correlation via conjugate multiply
    xcorr = np.fft.irfft(ref_fft * np.conj(tgt_fft))
    
    peak = np.argmax(xcorr)
    if peak > fft_size // 2:
        peak -= fft_size
    
    return peak

def main():
    parser = argparse.ArgumentParser(description="Auto-Sync Multi-Cam Audio via FFT Cross-Correlation")
    parser.add_argument("--master", required=True, help="Path to Master Audio/Lavalier file")
    parser.add_argument("--targets", nargs="+", required=True, help="Paths to Camera files to sync against Master")
    parser.add_argument("--duration", type=int, default=20, help="Seconds of audio to compare (default: 20)")
    args = parser.parse_args()

    SR = 16000

    print(f"[*] Extracting Master Reference: {args.master} (0-{args.duration}s)...")
    try:
        ref = extract_audio_np(args.master, 0, args.duration)
    except Exception as e:
        print(f"[!] Failed to extract master: {e}")
        return

    print("\n=== START CLIPS (vs Master at 0s) ===")
    offsets = {}
    for path in args.targets:
        if not os.path.exists(path):
            print(f"  [X] File not found: {path}")
            continue
            
        print(f"[*] Analyzing target: {path}")
        target = extract_audio_np(path, 0, args.duration + 10) # extract slightly more target
        
        lag = find_offset(ref, target)
        lag_sec = lag / SR
        
        offsets[path] = lag_sec
        name = os.path.basename(path)
        print(f"  {name}: lag={lag} samples = {lag_sec:.4f}s")
        print(f"    → Offset: {lag_sec:.4f}s (camera started {abs(lag_sec):.3f}s {'before' if lag_sec > 0 else 'after'} master)\n")

    print("\n=== FINAL OFFSET TABLE ===")
    for k, v in offsets.items():
        print(f"  {os.path.basename(k)}: {v:.4f}s")
        
    print("\n[+] Sync Complete.")

if __name__ == "__main__":
    main()
