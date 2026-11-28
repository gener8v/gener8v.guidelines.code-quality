import unittest

from cq_measure.codebase import scan_source
from cq_measure.structure.dependencies.imports.script_imports import (
    climb_of,
    script_imports,
)

SOURCE = """import a from './a';
import type { B } from "../b";
export * from './c';
const d = require('d');
const e = await import('./e');
const s = 'not an import';
"""


class ScriptImportsTest(unittest.TestCase):
    def test_finds_every_specifier_form(self):
        found = script_imports(scan_source(SOURCE))
        self.assertEqual([(i.line, i.specifier, i.type_only) for i in found], [
            (1, "./a", False), (2, "../b", True), (3, "./c", False), (4, "d", False), (5, "./e", False),
        ])

    def test_climb(self):
        self.assertEqual(climb_of("../../x"), 2)
        self.assertEqual(climb_of("./x"), 0)


if __name__ == "__main__":
    unittest.main()
