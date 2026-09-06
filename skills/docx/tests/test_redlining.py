"""Regression fixtures are temporary minimal XML/ZIP files, never user documents."""
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

DOCX_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(DOCX_ROOT))
from ooxml.scripts.validation.redlining import RedliningValidator
from scripts.document import Document

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def document(inner):
    return f'<w:document xmlns:w="{W}"><w:body><w:p>{inner}</w:p></w:body></w:document>'


def text(value):
    return f"<w:r><w:t>{value}</w:t></w:r>"


def insertion(value, author="Codex", revision_id="1"):
    return f'<w:ins w:author="{author}" w:id="{revision_id}">{text(value)}</w:ins>'


def deletion(value, author="Codex", revision_id="2"):
    return f'<w:del w:author="{author}" w:id="{revision_id}"><w:r><w:delText>{value}</w:delText></w:r></w:del>'


class RedliningTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.unpacked = self.root / "unpacked"
        (self.unpacked / "word").mkdir(parents=True)
        self.original = self.root / "original.docx"

    def fixture(self, original, modified):
        with zipfile.ZipFile(self.original, "w") as archive:
            archive.writestr("word/document.xml", document(original))
        (self.unpacked / "word" / "document.xml").write_text(document(modified), encoding="utf-8")

    def validate(self, **options):
        with redirect_stdout(StringIO()):
            return RedliningValidator(self.unpacked, self.original, **options).validate()

    def test_default_validates_claude_and_codex_insertions_and_deletions(self):
        for author in ("Claude", "Codex"):
            with self.subTest(author=author):
                self.fixture(text("before"), deletion("before", author) + insertion("after", author))
                self.assertTrue(self.validate())
                self.fixture(text("before"), text("untracked") + insertion("after", author))
                self.assertFalse(self.validate())

    def test_custom_author_and_explicit_author_set(self):
        self.fixture(text("base"), text("base") + insertion("a", "Editor A") + insertion("b", "Editor B"))
        self.assertTrue(self.validate(authors={"Editor A", "Editor B"}))
        self.assertFalse(self.validate(author="Editor A"))
        self.fixture(text("base"), text("base") + insertion("a", "Editor A"))
        self.assertTrue(self.validate(author="Editor A"))
        self.assertFalse(self.validate())

    def test_no_selected_author_edits_still_checks_untracked_text(self):
        self.fixture(text("before"), text("after"))
        self.assertFalse(self.validate())
        self.fixture(text("same"), text("same"))
        self.assertTrue(self.validate())

    def test_preserves_other_authors_deletion_text_and_metadata(self):
        baseline = text("base") + deletion("reviewed", "Reviewer", "42")
        for modified in (
            text("base") + deletion("tampered", "Reviewer", "42"),
            text("base") + deletion("reviewed", "Other", "42"),
            text("base") + deletion("reviewed", "Reviewer", "99"),
            text("base"),
        ):
            with self.subTest(modified=modified):
                self.fixture(baseline, modified + insertion("new"))
                self.assertFalse(self.validate(author="Codex"))

    def test_preserves_other_authors_insertion_and_allows_nested_rejection(self):
        baseline = insertion("reviewed", "Reviewer", "42")
        modified = '<w:ins w:author="Reviewer" w:id="42">' + deletion("reviewed") + "</w:ins>"
        self.fixture(baseline, modified)
        self.assertTrue(self.validate(author="Codex"))
        self.fixture(baseline, insertion("tampered", "Reviewer", "42") + insertion("new"))
        self.assertFalse(self.validate(author="Codex"))

    def test_explicit_author_does_not_treat_other_ai_as_this_operations_author(self):
        baseline = text("base") + insertion("prior", "Claude")
        self.fixture(baseline, text("base") + insertion("new", "Codex"))
        self.assertFalse(self.validate(author="Codex"))

    def test_malformed_missing_or_invalid_original_cannot_pass(self):
        self.fixture(text("base"), insertion("new"))
        (self.unpacked / "word" / "document.xml").write_text("<broken", encoding="utf-8")
        self.assertFalse(self.validate())
        self.fixture(text("base"), text("base"))
        self.original.write_bytes(b"not a zip")
        self.assertFalse(self.validate())
        self.original.unlink()
        self.assertFalse(self.validate())

    def test_zip_members_are_not_extracted(self):
        self.fixture(text("base"), text("base"))
        with zipfile.ZipFile(self.original, "a") as archive:
            archive.writestr("../outside.txt", "should never be extracted")
        self.assertTrue(self.validate())
        self.assertFalse((self.root / "outside.txt").exists())

    def test_unsupported_revision_types_do_not_claim_text_validation_succeeded(self):
        self.fixture(text("base"), text("base") + '<w:rPrChange w:author="Codex" w:id="3"/>')
        self.assertFalse(self.validate())

    def test_invalid_author_configuration_is_rejected(self):
        for options in ({"author": "", "authors": None}, {"authors": []}, {"authors": [None]}, {"author": "A", "authors": ["B"]}):
            with self.subTest(options=options), self.assertRaises(ValueError):
                RedliningValidator(self.unpacked, self.original, **options)

    def test_document_validate_passes_its_author_to_real_redlining_validator(self):
        self.fixture(text("base"), text("base") + insertion("new", "Editor A"))
        # Isolate schema validation because these fixtures intentionally contain only
        # document.xml; exercise the real Document method and redlining implementation.
        doc = Document.__new__(Document)
        doc.unpacked_path = self.unpacked
        doc.original_docx = self.original
        doc.author = "Editor A"
        with patch("scripts.document.DOCXSchemaValidator") as schema:
            schema.return_value.validate.return_value = True
            doc.validate()
            doc.author = "Editor B"
            with redirect_stdout(StringIO()), self.assertRaisesRegex(ValueError, "Redlining"):
                doc.validate()

    def test_cli_repeated_author_arguments_reach_the_real_validator(self):
        import importlib.util
        script_dir = DOCX_ROOT / "ooxml" / "scripts"
        sys.path.insert(0, str(script_dir))
        self.addCleanup(sys.path.remove, str(script_dir))
        spec = importlib.util.spec_from_file_location("docx_validate_cli", script_dir / "validate.py")
        cli = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cli)
        self.fixture(text("base"), text("base") + insertion("a", "Editor A") + insertion("b", "Editor B"))
        args = ["validate.py", str(self.unpacked), "--original", str(self.original), "--author", "Editor A", "--author", "Editor B"]
        with patch.object(cli, "DOCXSchemaValidator") as schema, patch.object(sys, "argv", args):
            schema.return_value.validate.return_value = True
            with redirect_stdout(StringIO()), self.assertRaises(SystemExit) as result:
                cli.main()
            self.assertEqual(0, result.exception.code)


if __name__ == "__main__":
    unittest.main()
