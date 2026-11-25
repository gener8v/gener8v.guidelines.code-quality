import unittest

from cq_measure.fixture_repository import findings_for


class DebugOutputTest(unittest.TestCase):
    def test_typescript_and_python(self):
        files = {"src/a.ts": "console.log(x);\nconsole.error(x);\ndebugger;\n", "src/b.py": "print(x)\nbreakpoint()\nimport pdb\npdb.set_trace()\n"}
        found = findings_for(files, "debug-output")
        self.assertEqual([(f.path, f.line) for f in found], [("src/a.ts", 1), ("src/a.ts", 3), ("src/b.py", 1), ("src/b.py", 2), ("src/b.py", 4)])

    def test_cli_entry_points_and_tests(self):
        files = {
            "scripts/build.ts": "console.log('done');\n",
            "src/tool.py": 'print("x")\nif __name__ == "__main__":\n    pass\n',
            "src/__main__.py": "print(1)\n",
            "src/a.test.ts": "console.log(1);\n",
        }
        self.assertEqual(findings_for(files, "debug-output"), [])


if __name__ == "__main__":
    unittest.main()
