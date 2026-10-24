#!/usr/bin/env python3
"""Universal video downloader helper with anti-bot impersonation and media verification."""

import argparse
import glob
import os
import shutil
import subprocess
import sys

def find_ffmpeg():
    # 1. Check system PATH
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg:
        return os.path.dirname(ffmpeg)
    
    # 2. Check common known locations on Windows
    candidates = [
        r"C:\Users\User\Downloads\ffmpeg\ffmpeg-2026-01-12-git-21a3e44fbe-full_build\bin",
        r"C:\ffmpeg\bin",
        r"C:\Program Files\ffmpeg\bin",
        r"C:\tools\ffmpeg\bin"
    ]
    for c in candidates:
        if os.path.exists(os.path.join(c, "ffmpeg.exe")):
            return c
    return None

def download(url, output_dir=None, quality="best", impersonate="chrome", cookies_browser=None):
    if not output_dir:
        # Default to I:\downloads if available, else user Downloads
        if os.path.exists("I:\\"):
            output_dir = r"I:\downloads"
        else:
            output_dir = os.path.expanduser("~/Downloads")
    
    os.makedirs(output_dir, exist_ok=True)
    
    ffmpeg_dir = find_ffmpeg()
    
    cmd = [
        "uvx",
        "--with", "yt-dlp[curl-cffi]",
        "yt-dlp",
        "--no-playlist",
        "--impersonate", impersonate,
        "-f", quality,
        "-o", os.path.join(output_dir, "%(title)s.%(ext)s"),
    ]
    
    if ffmpeg_dir:
        cmd.extend(["--ffmpeg-location", ffmpeg_dir])
    
    if cookies_browser:
        cmd.extend(["--cookies-from-browser", cookies_browser])
        
    cmd.append(url)
    
    print(f"Executing: {' '.join(cmd)}")
    res = subprocess.run(cmd)
    if res.returncode != 0:
        print(f"Download failed with returncode {res.returncode}", file=sys.stderr)
        return False
        
    print("Download completed successfully.")
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download video with anti-bot support")
    parser.add_argument("url", help="URL of the video to download")
    parser.add_argument("--output-dir", "-o", default=None, help="Target output directory")
    parser.add_argument("--quality", "-f", default="best", help="Format selection")
    parser.add_argument("--impersonate", default="chrome", help="Browser to impersonate")
    parser.add_argument("--cookies-browser", default=None, help="Browser to read cookies from")
    
    args = parser.parse_args()
    success = download(args.url, args.output_dir, args.quality, args.impersonate, args.cookies_browser)
    sys.exit(0 if success else 1)
