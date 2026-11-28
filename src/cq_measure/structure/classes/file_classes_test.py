import ast
import unittest

from cq_measure.codebase import CompilerResult, SourceFile, scan_source
from cq_measure.structure.classes.file_classes import classes_of
from cq_measure.testing import fixture_repo


def _scan(source):
    return scan_source(source.text)


class FileClassesTest(unittest.TestCase):
    def test_dispatch_by_language(self):
        files = {"a.py": "class A:\n    def f(self):\n        return 1\n", "b.ts": "class B { f() { return 1; } }\n", "d.go": ""}
        with fixture_repo(files) as root:
            python, script, go = (SourceFile(root, name) for name in files)
            self.assertEqual([c.name for c in classes_of(python, ast.parse(python.text), _scan)], ["A"])
            self.assertEqual([c.name for c in classes_of(script, None, _scan)], ["B"])
            self.assertEqual(classes_of(go, None, _scan), [])

    def test_uses_the_compiler_measures(self):
        item = {"name": "Port", "line": 2, "kind": "interface", "bases": ["Base"], "implements": [], "methods": ["send"]}
        compiled = CompilerResult(version="6.0.3", classes={"b.ts": [item]})
        with fixture_repo({"b.ts": ""}) as root:
            (info,) = classes_of(SourceFile(root, "b.ts"), None, _scan, compiled)
        self.assertEqual((info.name, info.bases, info.methods), ("Port", ("Base",), ("send",)))


if __name__ == "__main__":
    unittest.main()
