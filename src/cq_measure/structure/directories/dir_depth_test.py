import unittest

from cq_measure.testing import findings_for


class DirDepthTest(unittest.TestCase):
    def test_depth_below_package_root(self):
        found = findings_for({"a/b/c/d/e/f/x.py": "", "svc/pyproject.toml": "", "svc/a/b/c/d/e/x.py": ""}, "dir-depth")
        self.assertEqual([(f.path, f.severity) for f in found], [("a/b/c/d/e/f", "warn")])

    def test_java_source_root(self):
        self.assertEqual(findings_for({"src/main/java/com/acme/billing/x/Invoice.java": ""}, "dir-depth"), [])


if __name__ == "__main__":
    unittest.main()
