import unittest

from cq_measure.testing import findings_for


class ScriptPlacementTest(unittest.TestCase):
    def test_shell_script_in_source_dir(self):
        files = {"src/billing/run.sh": "", "src/billing/a.py": "", "scripts/deploy.sh": "", "install.sh": "", "docker/entry.sh": ""}
        self.assertEqual([f.path for f in findings_for(files, "script-placement")], ["src/billing/run.sh"])


if __name__ == "__main__":
    unittest.main()
