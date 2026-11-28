import ast
import unittest

from cq_measure.codebase import SourceFile, scan_source
from cq_measure.structure.functions.file_functions import functions_of
from cq_measure.testing import fixture_repo


def _scan(source):
    return scan_source(source.text)


class FileFunctionsTest(unittest.TestCase):
    def test_dispatch_by_language(self):
        files = {"a.py": "class A:\n    def f(self):\n        return 1\n", "b.ts": "class B { f() { return 1; } }\n", "c.d.ts": "", "d.go": ""}
        with fixture_repo(files) as root:
            python, script, declaration, go = (SourceFile(root, name) for name in files)
            tree = ast.parse(python.text)
            self.assertEqual([m.name for m in functions_of(python, tree, _scan)], ["f"])
            self.assertEqual([m.name for m in functions_of(script, None, _scan)], ["f"])
            self.assertEqual(functions_of(declaration, None, _scan), [])
            self.assertEqual(functions_of(go, None, _scan), [])


if __name__ == "__main__":
    unittest.main()
