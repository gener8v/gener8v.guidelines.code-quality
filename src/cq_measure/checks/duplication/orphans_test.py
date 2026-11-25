import unittest

from cq_measure.checks.duplication.orphans import reference_tokens
from cq_measure.fixture_repository import findings_for


class OrphanFileTest(unittest.TestCase):
    def test_unused_file(self):
        files = {"src/shop/__init__.py": "", "src/shop/lonely.py": "X = 1\n", "src/shop/used.py": "", "src/shop/main.py": "from shop import used\n"}
        self.assertEqual([f.path for f in findings_for(files, "orphan-file")], ["src/shop/lonely.py"])

    def test_entry_points_and_references(self):
        files = {
            "web/src/worker.ts": "", "web/src/app.ts": "new Worker('./worker.ts');\n", "web/index.ts": "import './src/app';\n",
            "tool.py": 'if __name__ == "__main__":\n    pass\n', "Dockerfile": "CMD python -m svc.server\n", "svc/server.py": "",
            "x.test.ts": "", "env.d.ts": "",
        }
        self.assertEqual(findings_for(files, "orphan-file"), [])

    def test_reference_tokens(self):
        self.assertEqual(reference_tokens("svc/api/server.py"), ["server.py", "api/server", "api.server"])


if __name__ == "__main__":
    unittest.main()
