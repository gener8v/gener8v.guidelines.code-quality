import unittest

from cq_measure.codebase.scanning.comments import (
    comments_of,
    hash_comments,
    python_comments,
)
from cq_measure.codebase.scanning.lexer import scan_source


class _File:
    def __init__(self, language, text):
        self.language = language
        self.text = text


class CommentsTest(unittest.TestCase):
    def test_python_comments_ignore_strings(self):
        found = python_comments('x = "# not a comment"  # real\n# own line\n')
        self.assertEqual([(c.line, c.text, c.own_line) for c in found], [(1, "real", False), (2, "own line", True)])

    def test_hash_comments_skip_shebang(self):
        found = hash_comments("#!/bin/sh\n# note\necho hi\n")
        self.assertEqual([(c.line, c.text) for c in found], [(2, "note")])

    def test_dispatch_by_language(self):
        script = comments_of(_File("typescript", "a(); // hi\n"), lambda f: scan_source(f.text))
        self.assertEqual([c.text for c in script], ["hi"])
        self.assertEqual(comments_of(_File(None, "# x\n"), None), [])


if __name__ == "__main__":
    unittest.main()
