"""
Validator for tracked changes in Word documents.
"""

import subprocess
import tempfile
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path


class RedliningValidator:
    """Validator for tracked changes in Word documents."""

    def __init__(self, unpacked_dir, original_docx, verbose=False, *, author=None, authors=None):
        """Validate edits for an explicit author or set of authors.

        Legacy callers default to Claude and Codex. Document passes its own author
        so edits by every other author must remain intact. This validates tracked
        text edits; schema/layout validation remains a separate responsibility.
        """
        if author is not None and authors is not None:
            raise ValueError("Specify author or authors, not both")
        selected = (author,) if author is not None else authors
        if selected is None:
            selected = ("Claude", "Codex")
        if isinstance(selected, str):
            selected = (selected,)
        self.authors = frozenset(selected)
        if not self.authors or any(not isinstance(value, str) or not value.strip() for value in self.authors):
            raise ValueError("Tracked-change authors must be non-empty strings")
        self.unpacked_dir = Path(unpacked_dir)
        self.original_docx = Path(original_docx)
        self.verbose = verbose
        self.namespaces = {
            "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
        }

    def validate(self):
        """Reject this operation's tracked edits and compare against the baseline.

        Always compare both documents, even when no selected-author edits exist:
        an untracked change or an unknown author must not produce a false pass.
        """
        modified_file = self.unpacked_dir / "word" / "document.xml"
        try:
            modified_root = ET.parse(modified_file).getroot()
            # Read only the required ZIP member; never extract user-supplied paths.
            with zipfile.ZipFile(self.original_docx, "r") as archive:
                original_root = ET.fromstring(archive.read("word/document.xml"))
        except (OSError, KeyError, zipfile.BadZipFile, ET.ParseError) as exc:
            print(f"FAILED - Cannot read document XML: {exc}")
            return False

        author_attr = f"{{{self.namespaces['w']}}}author"
        for root in (original_root, modified_root):
            for element in root.iter():
                local_tag = element.tag.rsplit("}", 1)[-1]
                if element.get(author_attr) in self.authors and (
                    local_tag.endswith("PrChange") or local_tag in {"moveFrom", "moveTo"}
                ):
                    print(f"FAILED - Tracked {local_tag} changes require a separate validator; text-edit validation is insufficient")
                    return False

        self._remove_authored_tracked_changes(original_root)
        self._remove_authored_tracked_changes(modified_root)

        # Text-only comparison misses deletion text and altered author/id metadata.
        # Preserve every remaining author's revision, allowing our rejected nested edits.
        if self._other_author_revisions(original_root) != self._other_author_revisions(modified_root):
            print("FAILED - Another author's tracked revision was added, removed, or modified")
            return False

        modified_text = self._extract_text_content(modified_root)
        original_text = self._extract_text_content(original_root)
        if modified_text != original_text:
            print(self._generate_detailed_diff(original_text, modified_text))
            return False
        if self.verbose:
            print("PASSED - Tracked text edits verified for: " + ", ".join(sorted(self.authors)))
        return True

    def _other_author_revisions(self, root):
        w = self.namespaces["w"]
        revision_tags = {f"{{{w}}}ins", f"{{{w}}}del"}
        text_tags = {f"{{{w}}}t", f"{{{w}}}delText", f"{{{w}}}instrText"}

        def signature(element):
            return (
                element.tag,
                tuple(sorted(element.attrib.items())),
                element.text if element.tag in text_tags else (element.text or "").strip(),
                tuple(signature(child) for child in element),
            )

        return [signature(element) for element in root.iter() if element.tag in revision_tags]

    def _generate_detailed_diff(self, original_text, modified_text):
        """Generate detailed word-level differences using git word diff."""
        error_parts = [
            "FAILED - Document text does not match after rejecting the selected authors' tracked changes",
            "",
            "Likely causes:",
            "  1. Modified text inside another author's <w:ins> or <w:del> tags",
            "  2. Made edits without proper tracked changes",
            "  3. Didn't nest <w:del> inside <w:ins> when deleting another's insertion",
            "",
            "For pre-redlined documents, use correct patterns:",
            "  - To reject another's INSERTION: Nest <w:del> inside their <w:ins>",
            "  - To restore another's DELETION: Add new <w:ins> AFTER their <w:del>",
            "",
        ]

        # Show git word diff
        git_diff = self._get_git_word_diff(original_text, modified_text)
        if git_diff:
            error_parts.extend(["Differences:", "============", git_diff])
        else:
            error_parts.append("Unable to generate word diff (git not available)")

        return "\n".join(error_parts)

    def _get_git_word_diff(self, original_text, modified_text):
        """Generate word diff using git with character-level precision."""
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)

                # Create two files
                original_file = temp_path / "original.txt"
                modified_file = temp_path / "modified.txt"

                original_file.write_text(original_text, encoding="utf-8")
                modified_file.write_text(modified_text, encoding="utf-8")

                # Try character-level diff first for precise differences
                result = subprocess.run(
                    [
                        "git",
                        "diff",
                        "--word-diff=plain",
                        "--word-diff-regex=.",  # Character-by-character diff
                        "-U0",  # Zero lines of context - show only changed lines
                        "--no-index",
                        str(original_file),
                        str(modified_file),
                    ],
                    capture_output=True,
                    text=True,
                )

                if result.stdout.strip():
                    # Clean up the output - remove git diff header lines
                    lines = result.stdout.split("\n")
                    # Skip the header lines (diff --git, index, +++, ---, @@)
                    content_lines = []
                    in_content = False
                    for line in lines:
                        if line.startswith("@@"):
                            in_content = True
                            continue
                        if in_content and line.strip():
                            content_lines.append(line)

                    if content_lines:
                        return "\n".join(content_lines)

                # Fallback to word-level diff if character-level is too verbose
                result = subprocess.run(
                    [
                        "git",
                        "diff",
                        "--word-diff=plain",
                        "-U0",  # Zero lines of context
                        "--no-index",
                        str(original_file),
                        str(modified_file),
                    ],
                    capture_output=True,
                    text=True,
                )

                if result.stdout.strip():
                    lines = result.stdout.split("\n")
                    content_lines = []
                    in_content = False
                    for line in lines:
                        if line.startswith("@@"):
                            in_content = True
                            continue
                        if in_content and line.strip():
                            content_lines.append(line)
                    return "\n".join(content_lines)

        except (subprocess.CalledProcessError, FileNotFoundError, Exception):
            # Git not available or other error, return None to use fallback
            pass

        return None

    def _remove_authored_tracked_changes(self, root):
        """Reject insertions and restore deletions for the selected authors."""
        ins_tag = f"{{{self.namespaces['w']}}}ins"
        del_tag = f"{{{self.namespaces['w']}}}del"
        author_attr = f"{{{self.namespaces['w']}}}author"

        # Remove w:ins elements
        for parent in root.iter():
            to_remove = []
            for child in parent:
                if child.tag == ins_tag and child.get(author_attr) in self.authors:
                    to_remove.append(child)
            for elem in to_remove:
                parent.remove(elem)

        # Restore deleted content only for the selected authors
        deltext_tag = f"{{{self.namespaces['w']}}}delText"
        t_tag = f"{{{self.namespaces['w']}}}t"

        for parent in root.iter():
            to_process = []
            for child in parent:
                if child.tag == del_tag and child.get(author_attr) in self.authors:
                    to_process.append((child, list(parent).index(child)))

            # Process in reverse order to maintain indices
            for del_elem, del_index in reversed(to_process):
                # Convert w:delText to w:t before moving
                for elem in del_elem.iter():
                    if elem.tag == deltext_tag:
                        elem.tag = t_tag

                # Move all children of w:del to its parent before removing w:del
                for child in reversed(list(del_elem)):
                    parent.insert(del_index, child)
                parent.remove(del_elem)

    def _extract_text_content(self, root):
        """Extract text content from Word XML, preserving paragraph structure.

        Empty paragraphs are skipped to avoid false positives when tracked
        insertions add only structural elements without text content.
        """
        p_tag = f"{{{self.namespaces['w']}}}p"
        t_tag = f"{{{self.namespaces['w']}}}t"

        paragraphs = []
        for p_elem in root.findall(f".//{p_tag}"):
            # Get all text elements within this paragraph
            text_parts = []
            for t_elem in p_elem.findall(f".//{t_tag}"):
                if t_elem.text:
                    text_parts.append(t_elem.text)
            paragraph_text = "".join(text_parts)
            # Skip empty paragraphs - they don't affect content validation
            if paragraph_text:
                paragraphs.append(paragraph_text)

        return "\n".join(paragraphs)


if __name__ == "__main__":
    raise RuntimeError("This module should not be run directly.")
