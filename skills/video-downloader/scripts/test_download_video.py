"""Offline downloader contract tests; no website or browser is accessed."""

import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("download_video", Path(__file__).with_name("download_video.py"))
video = importlib.util.module_from_spec(spec)
spec.loader.exec_module(video)

MEDIA = {"streams": [{"codec_type": "video", "codec_name": "h264", "width": 1920, "height": 1080},
                      {"codec_type": "audio", "codec_name": "aac"}], "format": {"duration": "2.5"}}


class DownloadTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.output = self.directory / "繁體中文_日本語.mp4"
        self.media = copy.deepcopy(MEDIA)
        self.calls = []

    def run_process(self, cmd, **kwargs):
        self.calls.append((cmd, kwargs))
        if cmd[0] == "uvx":
            self.output.write_bytes(b"media")
            manifest = Path(cmd[cmd.index("--print-to-file") + 2])
            manifest.write_text(str(self.output) + "\n", encoding="utf-8")
            return SimpleNamespace(returncode=0)
        return SimpleNamespace(returncode=0, stdout=json.dumps(self.media))

    def download(self, runner=None, **kwargs):
        with patch.object(video, "find_ffmpeg", return_value="/ffmpeg"), \
             patch.object(video, "find_ffprobe", return_value="ffprobe"), \
             patch.object(video.subprocess, "run", side_effect=runner or self.run_process):
            return video.download("https://example.invalid/video", str(self.directory), **kwargs)

    def test_best_format_unicode_output_and_probe_are_used(self):
        self.assertTrue(self.download(cookies_browser="chrome"))
        cmd, options = self.calls[0]
        self.assertEqual(cmd[cmd.index("-f") + 1], "bestvideo*+bestaudio/best")
        self.assertIn("--no-simulate", cmd)
        self.assertIn("--cookies-from-browser", cmd)
        self.assertEqual(options["env"]["PYTHONUTF8"], "1")
        self.assertEqual(self.calls[1][0][-1], str(self.output))
        self.assertEqual(self.calls[1][1]["timeout"], 60)

    def test_custom_format_is_preserved(self):
        self.assertTrue(self.download(quality="best[height<=720]"))
        self.assertEqual(self.calls[0][0][self.calls[0][0].index("-f") + 1], "best[height<=720]")

    def test_missing_audio_is_failure_and_preserves_file(self):
        self.media["streams"] = self.media["streams"][:1]
        self.assertFalse(self.download())
        self.assertTrue(self.output.exists())

    def test_missing_video_is_failure(self):
        self.media["streams"] = self.media["streams"][1:]
        self.assertFalse(self.download())

    def test_invalid_resolution_is_failure(self):
        self.media["streams"][0]["height"] = 0
        self.assertFalse(self.download())

    def test_invalid_duration_is_failure(self):
        for duration in ("0", "NaN", "inf", "N/A"):
            with self.subTest(duration=duration):
                self.media["format"]["duration"] = duration
                self.assertFalse(self.download())

    def test_missing_output_list_is_failure(self):
        self.assertFalse(self.download(runner=lambda *a, **k: SimpleNamespace(returncode=0)))

    def test_missing_and_empty_files_are_failure(self):
        for exists in (False, True):
            with self.subTest(exists=exists):
                def runner(cmd, **kwargs):
                    manifest = Path(cmd[cmd.index("--print-to-file") + 2])
                    manifest.write_text(str(self.output) + "\n", encoding="utf-8")
                    if exists:
                        self.output.write_bytes(b"")
                    return SimpleNamespace(returncode=0)
                self.assertFalse(self.download(runner=runner))

    def test_nonzero_downloader_status_is_failure(self):
        self.assertFalse(self.download(runner=lambda *a, **k: SimpleNamespace(returncode=1)))

    def test_bad_probe_or_timeout_is_failure(self):
        for failure in ("bad-json", "nonzero", "timeout"):
            with self.subTest(failure=failure):
                def runner(cmd, **kwargs):
                    if cmd[0] == "uvx":
                        return self.run_process(cmd, **kwargs)
                    if failure == "timeout":
                        raise subprocess.TimeoutExpired(cmd, 60)
                    return SimpleNamespace(returncode=1 if failure == "nonzero" else 0, stdout="bad")
                self.assertFalse(self.download(runner=runner))

    def test_missing_probe_stops_before_download(self):
        with patch.object(video, "find_ffmpeg", return_value=None), \
             patch.object(video, "find_ffprobe", return_value=None), \
             patch.object(video.subprocess, "run") as run:
            self.assertFalse(video.download("https://example.invalid", str(self.directory)))
            run.assert_not_called()

    def test_output_outside_requested_directory_is_rejected(self):
        def runner(cmd, **kwargs):
            manifest = Path(cmd[cmd.index("--print-to-file") + 2])
            manifest.write_text(str(self.directory.parent / "outside.mp4") + "\n", encoding="utf-8")
            return SimpleNamespace(returncode=0)
        self.assertFalse(self.download(runner=runner))

    def test_cli_failure_returns_nonzero(self):
        with patch.object(video, "download", return_value=False):
            self.assertEqual(video.main(["https://example.invalid"]), 1)


if __name__ == "__main__":
    unittest.main()
