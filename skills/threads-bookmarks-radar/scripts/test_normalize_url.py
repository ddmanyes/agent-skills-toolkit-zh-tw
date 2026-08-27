import importlib.util
import pathlib
import unittest


MODULE_PATH = pathlib.Path(__file__).with_name("normalize_url.py")
SPEC = importlib.util.spec_from_file_location("threads_normalize_url", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class NormalizeThreadsUrlTests(unittest.TestCase):
    def test_keeps_canonical_post(self):
        url = "https://www.threads.com/@example_user/post/DcXP5pDjY7c"
        self.assertEqual(MODULE.normalize_url(url), url)

    def test_normalizes_threads_net_and_removes_query(self):
        url = "https://threads.net/@example.user/post/ABC_123-?xmt=AQG#reply"
        expected = "https://www.threads.com/@example.user/post/ABC_123-"
        self.assertEqual(MODULE.normalize_url(url), expected)

    def test_rejects_saved_page(self):
        with self.assertRaisesRegex(ValueError, "Threads post URL"):
            MODULE.normalize_url("https://www.threads.com/saved/")

    def test_rejects_other_host(self):
        with self.assertRaisesRegex(ValueError, "Threads post URL"):
            MODULE.normalize_url("https://example.com/@user/post/ABC")


if __name__ == "__main__":
    unittest.main()
