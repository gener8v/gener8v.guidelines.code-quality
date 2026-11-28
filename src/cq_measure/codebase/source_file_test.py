import unittest

from cq_measure.codebase.source_file import SourceFile
from cq_measure.testing import fixture_repo


class SourceFileTest(unittest.TestCase):
    def test_reads_text_and_counts_non_blank_lines(self):
        with fixture_repo({"src/a.py": "x = 1\n\n  \ny = 2\n"}) as root:
            source = SourceFile(root, "src/a.py")
            self.assertEqual(source.nonblank, 2)
            self.assertEqual((source.name, source.stem, source.directory, source.language), ("a.py", "a", "src", "python"))
            self.assertIn("a.py", repr(source))


if __name__ == "__main__":
    unittest.main()
