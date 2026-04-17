#!/bin/bash
# Master V1 Look Function
# Captures the main monitor (LG TV / Right Screen) silently

DIR="/Volumes/WORK 2TB/WORK 2026/MASTER V1/.tmp/screenshots"
mkdir -p "$DIR"

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
RAW_FILENAME="$DIR/master_vision_$TIMESTAMP.jpg"

# Take a silent (-x) screenshot of the main monitor (-m) in JPEG format
screencapture -x -m -t jpg "$RAW_FILENAME"

echo "SCREENSHOT: $RAW_FILENAME"
