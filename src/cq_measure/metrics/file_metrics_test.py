import ast
import unittest

from cq_measure.fixture_repository import fixture_repo
from cq_measure.metrics.file_metrics import classes_of, functions_of
from cq_measure.source.lexer import scan_source
from cq_measure.source.source_file import SourceFile


def _scan(source):
    return scan_source(source.text)


class FileMetricsTest(unittest.TestCase):
    def test_dispatch_by_language(self):
        files = {"a.py": "class A:\n    def f(self):\n        return 1\n", "b.ts": "class B { f() { return 1; } }\n", "c.d.ts": "", "d.go": ""}
        with fixture_repo(files) as root:
            python, script, declaration, go = (SourceFile(root, name) for name in files)
            tree = ast.parse(python.text)
            self.assertEqual([m.name for m in functions_of(python, tree, _scan)], ["f"])
            self.assertEqual([c.name for c in classes_of(python, tree, _scan)], ["A"])
            self.assertEqual([m.name for m in functions_of(script, None, _scan)], ["f"])
            self.assertEqual([c.name for c in classes_of(script, None, _scan)], ["B"])
            self.assertEqual(functions_of(declaration, None, _scan), [])
            self.assertEqual(classes_of(go, None, _scan), [])


if __name__ == "__main__":
    unittest.main()
