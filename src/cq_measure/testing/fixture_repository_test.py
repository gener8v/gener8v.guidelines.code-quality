import unittest

from cq_measure.testing.fixture_repository import findings_for, fixture_repo


class FixtureRepositoryTest(unittest.TestCase):
    def test_writes_files_and_cleans_up(self):
        with fixture_repo({"a/b.txt": "hi"}) as root:
            self.assertEqual((root / "a/b.txt").read_text(), "hi")
        self.assertFalse(root.exists())

    def test_findings_for_runs_one_check(self):
        found = findings_for({"a.py": "x = 1\n" * 301}, "file-lines")
        self.assertEqual([f.check for f in found], ["file-lines"])


if __name__ == "__main__":
    unittest.main()
