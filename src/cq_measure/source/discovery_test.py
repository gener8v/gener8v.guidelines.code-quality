import unittest

from cq_measure.fixture_repository import fixture_repo
from cq_measure.source.discovery import discover, git_files, is_text_file, walk_files


class DiscoveryTest(unittest.TestCase):
    def test_walk_applies_ignore_globs_and_skips_binary(self):
        files = {"src/a.py": "x = 1\n", "node_modules/p/i.js": "", "pkg/dist/b.js": "", "img.bin": "\0\0"}
        with fixture_repo(files) as root:
            self.assertEqual(discover(root, ["node_modules/**", "dist/**"]), ["src/a.py"])

    def test_walk_lists_files_and_skips_git(self):
        with fixture_repo({".git/HEAD": "ref", "a/b.txt": "x"}) as root:
            self.assertEqual(walk_files(root), ["a/b.txt"])

    def test_git_files_is_none_outside_a_work_tree(self):
        with fixture_repo({"a.py": ""}) as root:
            self.assertIsNone(git_files(root))

    def test_text_file_rules(self):
        with fixture_repo({"big.txt": "x" * (1024 * 1024 + 1), "ok.txt": "x"}) as root:
            self.assertFalse(is_text_file(root / "big.txt"))
            self.assertTrue(is_text_file(root / "ok.txt"))
            self.assertFalse(is_text_file(root / "missing.txt"))


if __name__ == "__main__":
    unittest.main()
