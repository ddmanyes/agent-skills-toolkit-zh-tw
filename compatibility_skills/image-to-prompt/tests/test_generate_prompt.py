"""Use temporary image files and mocked HTTP/model boundaries only."""
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import URLError

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import generate_prompt as prompt


class PromptTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.picture = Path(self.temp.name) / "picture.png"
        self.picture.write_bytes(b"temporary input; no network use")

    def run_main(self, args):
        self.out, self.err = StringIO(), StringIO()
        with redirect_stdout(self.out), redirect_stderr(self.err):
            return prompt.main(args)

    def test_missing_image_and_unknown_mode_stop_before_network(self):
        with patch.object(prompt, "check_server_vision") as health:
            self.assertEqual(2, self.run_main([str(self.picture.parent / "missing.png")]))
            self.assertEqual(2, self.run_main([str(self.picture), "unknown"]))
            health.assert_not_called()

    def test_help_does_not_connect(self):
        with patch.object(prompt, "check_server_vision") as health:
            self.assertEqual(0, self.run_main(["--help"]))
            health.assert_not_called()

    def test_health_failure_does_not_invent_launcher(self):
        with patch.object(prompt, "check_server_vision", return_value=False), patch.object(prompt, "call_vision") as call:
            self.assertEqual(1, self.run_main([str(self.picture)]))
            call.assert_not_called()
        self.assertNotIn("switch-model.ps1", self.err.getvalue())

    def test_health_success_does_not_mask_unsupported_vision(self):
        with patch.object(prompt, "check_server_vision", return_value=True), patch.object(prompt, "call_vision", side_effect=URLError("image input unsupported")):
            self.assertEqual(1, self.run_main([str(self.picture)]))
        self.assertIn("does not verify vision", self.err.getvalue())

    def test_empty_and_incomplete_outputs_are_failures(self):
        for result in ("", "English (natural description): partial"):
            with self.subTest(result=result), patch.object(prompt, "check_server_vision", return_value=True), patch.object(prompt, "call_vision", return_value=result):
                self.assertEqual(1, self.run_main([str(self.picture)]))

    def test_supported_mode_and_extra_prompt_are_preserved(self):
        with patch.object(prompt, "check_server_vision", return_value=True), patch.object(prompt, "call_vision", return_value="visible scene") as call:
            self.assertEqual(0, self.run_main([str(self.picture), "fidelity", "preserve", "lighting"]))
            call.assert_called_once_with(str(self.picture.resolve()), "fidelity", extra_prompt="preserve lighting")

    def test_bilingual_json_requires_metadata_schema(self):
        prefix = "English (natural description): visible scene.\n中文（自然描写）：" + "可見畫面中的物件。" * 12 + "\n"
        self.assertFalse(prompt._is_manga_complete(prefix + "{}"))
        metadata = {key:"observed" for key in ["shot", "framing", "angle", "mood", "lighting", "appearance", "clothing", "background"]}
        metadata.update(orientation="portrait", has_character=False, character_count=0, style_tags=[])
        self.assertTrue(prompt._is_manga_complete(prefix + json.dumps(metadata)))
        metadata["has_character"] = "false"
        self.assertFalse(prompt._is_manga_complete(prefix + json.dumps(metadata)))

    def test_image_encoding_reuses_original_mime_handling(self):
        encoded, mime = prompt.encode_image(str(self.picture))
        self.assertTrue(encoded)
        self.assertEqual("image/png", mime)
        invalid = self.picture.with_suffix(".txt")
        invalid.write_text("input", encoding="utf-8")
        with self.assertRaises(ValueError):
            prompt.encode_image(str(invalid))


if __name__ == "__main__":
    unittest.main()
