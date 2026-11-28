import unittest

from cq_measure.testing import findings_for


class RootFilesTest(unittest.TestCase):
    def test_counts_non_dot_files_per_package_root(self):
        files = {f"f{i}.txt": "" for i in range(16)}
        files.update({".env.example": "", "web/package.json": "{}"})
        files.update({f"web/n{i}.md": "" for i in range(26)})
        found = findings_for(files, "root-files")
        self.assertEqual([(f.path, f.severity) for f in found], [(".", "warn"), ("web", "fail")])

    def test_small_root(self):
        self.assertEqual(findings_for({"README.md": "", "LICENSE": ""}, "root-files"), [])


class RootSourceTest(unittest.TestCase):
    def test_source_module_at_root(self):
        found = findings_for({"app.py": "", "pkg/package.json": "{}", "pkg/server.ts": ""}, "root-source")
        self.assertEqual(sorted(f.path for f in found), ["app.py", "pkg/server.ts"])

    def test_tool_configuration_is_allowed(self):
        files = {"vite.config.ts": "", "conftest.py": "", "setup.py": "", "main.go": "", "deploy.sh": "", "src/app.py": ""}
        self.assertEqual(findings_for(files, "root-source"), [])


if __name__ == "__main__":
    unittest.main()
