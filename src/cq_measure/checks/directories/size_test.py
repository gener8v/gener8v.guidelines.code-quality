import unittest

from cq_measure.fixture_repository import findings_for


class DirFilesTest(unittest.TestCase):
    def test_counts_source_files_not_tests(self):
        files = {f"src/m{i}.py": "" for i in range(13)}
        files.update({f"src/m{i}_test.py": "" for i in range(13)})
        files["src/__init__.py"] = ""
        found = findings_for(files, "dir-files")
        self.assertEqual([(f.path, f.severity) for f in found], [("src", "warn")])
        self.assertEqual(findings_for({f"src/m{i}.py": "" for i in range(12)}, "dir-files"), [])


class DirSubdirsTest(unittest.TestCase):
    def test_counts_subdirectories(self):
        files = {f"src/d{i}/a.py": "" for i in range(21)}
        self.assertEqual([(f.path, f.severity) for f in findings_for(files, "dir-subdirs")], [("src", "fail")])
        self.assertEqual(findings_for({f"src/d{i}/a.py": "" for i in range(12)}, "dir-subdirs"), [])


class DirDepthTest(unittest.TestCase):
    def test_depth_below_package_root(self):
        found = findings_for({"a/b/c/d/e/f/x.py": "", "svc/pyproject.toml": "", "svc/a/b/c/d/e/x.py": ""}, "dir-depth")
        self.assertEqual([(f.path, f.severity) for f in found], [("a/b/c/d/e/f", "warn")])

    def test_java_source_root(self):
        self.assertEqual(findings_for({"src/main/java/com/acme/billing/x/Invoice.java": ""}, "dir-depth"), [])


if __name__ == "__main__":
    unittest.main()
