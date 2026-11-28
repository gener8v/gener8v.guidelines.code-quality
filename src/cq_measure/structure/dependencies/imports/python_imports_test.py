import ast
import unittest

from cq_measure.structure.dependencies.imports.python_imports import python_imports

SOURCE = """
import os.path
from ..billing import invoice, _round
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from accounts import Account
"""


class PythonImportsTest(unittest.TestCase):
    def test_extracts_modules_levels_names_and_type_only(self):
        found = python_imports(ast.parse(SOURCE))
        summary = [(i.module, i.level, i.names, i.type_only) for i in found]
        self.assertIn(("os.path", 0, (), False), summary)
        self.assertIn(("billing", 2, ("invoice", "_round"), False), summary)
        self.assertIn(("accounts", 0, ("Account",), True), summary)


if __name__ == "__main__":
    unittest.main()
