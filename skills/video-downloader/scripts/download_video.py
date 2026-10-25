#!/usr/bin/env python3
"""Download the best available video/audio and verify the resulting media."""

import argparse
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

DEFAULT_FORMAT = "bestvideo*+bestaudio/best"


def find_ffmpeg():
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg:
        return str(Path(ffmpeg).parent)
    for directory in (
        r"C:\Users\User\Downloads\ffmpeg\ffmpeg-2026-01-12-git-21a3e44fbe-full_build\bin",
        r"C:\ffmpeg\bin", r"C:\Program Files\ffmpeg\bin", r"C:\tools\ffmpeg\bin",
    ):
        if (Path(directory) / "ffmpeg.exe").is_file():
            return directory
    return None


def find_ffprobe(ffmpeg_dir):
    if ffmpeg_dir:
        for name in ("ffprobe.exe", "ffprobe"):
            candidate = Path(ffmpeg_dir) / name
            if candidate.is_file():
                return str(candidate)
    return shutil.which("ffprobe")


def verify_media(path, ffprobe):
    if not path.is_file() or path.stat().st_size <= 0:
        raise ValueError("Output file is missing or empty")
    probe = subprocess.run(
        [ffprobe, "-v", "error", "-show_format", "-show_streams", "-of", "json", str(path)],
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60,
    )
    if probe.returncode:
        raise ValueError("ffprobe could not read the output")
    data = json.loads(probe.stdout)
    if not isinstance(data, dict):
        raise ValueError("ffprobe returned an invalid media description")
    streams = data.get("streams", [])
    videos = [s for s in streams if s.get("codec_type") == "video" and not s.get("disposition", {}).get("attached_pic")]
    if not any(s.get("codec_name") and int(s.get("width", 0)) > 0 and int(s.get("height", 0)) > 0 for s in videos):
        raise ValueError("Output has no valid video stream")
    if not any(s.get("codec_type") == "audio" and s.get("codec_name") for s in streams):
        raise ValueError("Output has no valid audio stream")
    durations = [data.get("format", {}).get("duration"), *(s.get("duration") for s in streams)]
    for duration in durations:
        try:
            if math.isfinite(float(duration)) and float(duration) > 0:
                return
        except (TypeError, ValueError):
            continue
    raise ValueError("Output has no positive finite duration")


def download(url, output_dir=None, quality=DEFAULT_FORMAT, impersonate="chrome", cookies_browser=None):
    directory = Path(output_dir) if output_dir else (Path("I:/downloads") if Path("I:/").exists() else Path.home() / "Downloads")
    directory = directory.expanduser().resolve()
    directory.mkdir(parents=True, exist_ok=True)
    ffmpeg_dir = find_ffmpeg()
    ffprobe = find_ffprobe(ffmpeg_dir)
    if not ffmpeg_dir or not ffprobe:
        print("ffmpeg and ffprobe are required for merging and media verification; install both and retry.", file=sys.stderr)
        return False
    try:
        with tempfile.TemporaryDirectory(prefix=".download-check-", dir=directory) as temporary:
            manifest = Path(temporary) / "outputs.txt"
            cmd = [
                "uvx", "--with", "yt-dlp[curl-cffi]", "yt-dlp",
                "--no-playlist", "--no-simulate", "--impersonate", impersonate,
                "-f", quality, "-o", str(directory / "%(title)s.%(ext)s"),
                "--print-to-file", "after_move:%(filepath)s", str(manifest),
            ]
            if ffmpeg_dir:
                cmd.extend(["--ffmpeg-location", ffmpeg_dir])
            if cookies_browser:
                cmd.extend(["--cookies-from-browser", cookies_browser])
            cmd.extend(["--", url])
            # Do not print URLs that may contain tokens. yt-dlp owns Unicode filenames.
            env = {**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"}
            result = subprocess.run(cmd, env=env)
            if result.returncode:
                print(f"Download failed with returncode {result.returncode}", file=sys.stderr)
                return False
            if not manifest.is_file():
                raise ValueError("Downloader did not report any output file")
            outputs = [Path(line).expanduser() for line in manifest.read_text(encoding="utf-8").splitlines() if line.strip()]
            if not outputs:
                raise ValueError("Downloader reported an empty output list")
            for output in outputs:
                path = (output if output.is_absolute() else directory / output).resolve()
                if not path.is_relative_to(directory):
                    raise ValueError("Downloader reported an output outside the requested directory")
                verify_media(path, ffprobe)
            print(f"Download and media verification completed: {len(outputs)} file(s).")
            return True
    except (OSError, ValueError, TypeError, subprocess.SubprocessError) as exc:
        print(f"Download/verification failed: {exc}. Existing media files were preserved.", file=sys.stderr)
        return False


def main(argv=None):
    parser = argparse.ArgumentParser(description="Download video with browser impersonation and media verification")
    parser.add_argument("url", help="URL of the video to download")
    parser.add_argument("--output-dir", "-o", default=None, help="Target output directory")
    parser.add_argument("--quality", "-f", default=DEFAULT_FORMAT, help="yt-dlp format selection")
    parser.add_argument("--impersonate", default="chrome", help="Browser to impersonate")
    parser.add_argument("--cookies-browser", default=None, help="Browser to read cookies from")
    args = parser.parse_args(argv)
    return 0 if download(args.url, args.output_dir, args.quality, args.impersonate, args.cookies_browser) else 1


if __name__ == "__main__":
    raise SystemExit(main())
