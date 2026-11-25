import unittest

from cq_measure.checks.packages.cycles import shortest_cycle, sibling_pair
from cq_measure.fixture_repository import findings_for


class ImportCycleTest(unittest.TestCase):
    def test_directories_in_a_cycle(self):
        files = {"src/billing/a.ts": "import b from '../accounts/b';\n", "src/accounts/b.ts": "import a from '../billing/sub/c';\n", "src/billing/sub/c.ts": ""}
        found = findings_for(files, "import-cycle")
        self.assertEqual(len(found), 1)
        self.assertIn("src/accounts -> src/billing -> src/accounts", found[0].message)

    def test_one_way_and_type_only(self):
        files = {"src/billing/a.ts": "import b from '../accounts/b';\n", "src/accounts/b.ts": "import type { A } from '../billing/a';\n"}
        self.assertEqual(findings_for(files, "import-cycle"), [])

    def test_helpers(self):
        self.assertEqual(sibling_pair("src/a/x", "src/b"), ("src/a", "src/b"))
        self.assertIsNone(sibling_pair("src", "src/b"))
        self.assertEqual(shortest_cycle({"a": ["b"], "b": ["a"]}, ["a", "b"]), ["a", "b", "a"])


class FileCycleTest(unittest.TestCase):
    def test_files_in_a_cycle(self):
        files = {"pkg/a.py": "from pkg import b\n", "pkg/b.py": "from pkg import a\n"}
        found = findings_for(files, "file-cycle")
        self.assertEqual([(f.path, f.severity) for f in found], [("pkg/a.py", "warn")])
        self.assertEqual(findings_for({"pkg/a.py": "from pkg import b\n", "pkg/b.py": ""}, "file-cycle"), [])


if __name__ == "__main__":
    unittest.main()
