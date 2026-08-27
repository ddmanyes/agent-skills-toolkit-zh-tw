import importlib.util
import pathlib
import unittest


MODULE_PATH = pathlib.Path(__file__).with_name("normalize_url.py")
SPEC = importlib.util.spec_from_file_location("x_normalize_url", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class NormalizeXUrlTests(unittest.TestCase):
    def test_keeps_canonical_status(self):
        url = "https://x.com/example_user/status/2090964415034347719"
        self.assertEqual(MODULE.normalize_url(url), url)

    def test_normalizes_twitter_media_url(self):
        url = "https://twitter.com/example/status/2090964415034347719/photo/1?s=20#media"
        expected = "https://x.com/example/status/2090964415034347719"
        self.assertEqual(MODULE.normalize_url(url), expected)

    def test_rejects_bookmark_page(self):
        with self.assertRaisesRegex(ValueError, "X status URL"):
            MODULE.normalize_url("https://x.com/i/bookmarks")

    def test_rejects_non_numeric_status_id(self):
        with self.assertRaisesRegex(ValueError, "X status URL"):
            MODULE.normalize_url("https://x.com/example/status/not-a-number")


if __name__ == "__main__":
    unittest.main()
