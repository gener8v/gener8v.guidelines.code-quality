import unittest

from cq_measure.config import load_defaults
from cq_measure.findings import Finding
from cq_measure.fixture_repository import fixture_repo
from cq_measure.runner import UsageError, changed_files, keep_paths, measure


class RunnerTest(unittest.TestCase):
    def test_runs_enabled_checks_only(self):
        config = load_defaults()
        config["checks"]["file-lines"]["enabled"] = False
        with fixture_repo({"a.py": "x = 1\n" * 600}) as root:
            self.assertEqual(measure(root, config, {"file-lines"}), [])
            self.assertEqual(len(measure(root, load_defaults(), {"file-lines"})), 1)

    def test_keep_paths(self):
        findings = [Finding("src/a.py", 1, "x", "c", "warn", "m"), Finding("docs/b.py", 1, "x", "c", "warn", "m")]
        self.assertEqual([f.path for f in keep_paths(findings, ["src/"])], ["src/a.py"])
        self.assertEqual(len(keep_paths(findings, ["."])), 2)

    def test_changed_files_needs_git(self):
        with fixture_repo({"a.py": ""}) as root:
            with self.assertRaises(UsageError):
                changed_files(root, "HEAD")


if __name__ == "__main__":
    unittest.main()
