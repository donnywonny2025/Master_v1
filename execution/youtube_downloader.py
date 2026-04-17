import os
import sys
import subprocess
import argparse

# Path definitions
BIN_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bin", "yt-dlp")
DOWNLOADS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "DOWNLOADS")

def ensure_dirs():
    os.makedirs(DOWNLOADS_DIR, exist_ok=True)
    if not os.path.exists(BIN_PATH):
        print(f"[ERROR] yt-dlp binary missing at {BIN_PATH}")
        print("Please ensure the framework initialization downloaded it correctly.")
        sys.exit(1)

def get_next_version(downloads_dir):
    """Scan DOWNLOADS/ to find the next V-number."""
    import re
    max_v = 0
    pattern = re.compile(r"^DOWNLOAD_V(\d+)_")
    if os.path.exists(downloads_dir):
        for f in os.listdir(downloads_dir):
            match = pattern.match(f)
            if match:
                v = int(match.group(1))
                if v > max_v: max_v = v
    return max_v + 1

def download(url, audio_only=False):
    ensure_dirs()
    
    print(f"[*] Initializing Downloader Framework for: {url}")
    print(f"[*] Target Directory: {DOWNLOADS_DIR}")
    
    import datetime
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    version = get_next_version(DOWNLOADS_DIR)
    
    # We output to DOWNLOADS/DOWNLOAD_V[X]_[Timestamp]_[Title].%(ext)s
    out_name = f"DOWNLOAD_V{version}_{ts}_%(title)s.%(ext)s"
    output_template = os.path.join(DOWNLOADS_DIR, out_name)
    
    cmd = [BIN_PATH, url, "-o", output_template]
    
    if audio_only:
        print("[*] Mode: Audio-Only Extraction")
        cmd.extend(["-x", "--audio-format", "mp3"])
    else:
        print("[*] Mode: Maximum Quality Video")
        # Ensure it merges the best video/audio natively into an MP4 if possible.
        cmd.extend(["-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"])
        
    try:
        subprocess.run(cmd, check=True)
        print("[+] Download Completed Successfully!")
    except subprocess.CalledProcessError as e:
        print(f"[-] Execution Failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Master V1 YouTube Terminal Downloader")
    parser.add_argument("url", help="The URL to download (YouTube, Twitter, generic video urls)")
    parser.add_argument("--audio", action="store_true", help="Download and extract as MP3 Audio-Only")
    
    args = parser.parse_args()
    download(args.url, audio_only=args.audio)
