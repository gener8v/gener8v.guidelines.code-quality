import unittest

from cq_measure.testing import findings_for


class SingleChildDirTest(unittest.TestCase):
    def test_lone_child(self):
        self.assertEqual([f.path for f in findings_for({"docs/adr/a.md": ""}, "single-child-dir")], ["docs"])

    def test_exemptions(self):
        files = {"src/pkg/a.py": "", "src/main/java/com/A.java": "", "cmd/server/main.go": "", "app/settings/profile/page.tsx": ""}
        self.assertEqual(findings_for(files, "single-child-dir"), [])


if __name__ == "__main__":
    unittest.main()
