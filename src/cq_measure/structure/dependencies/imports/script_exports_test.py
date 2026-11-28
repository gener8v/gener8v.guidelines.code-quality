import unittest

from cq_measure.codebase import scan_source
from cq_measure.structure.dependencies.imports.script_exports import script_exports

SOURCE = """export function Button() { return null; }
export const Card = ({ x }) => x;
export const variants = cva('a');
export const Styles = { a: 1 };
export default class Store {}
export interface Props { a: string }
const a = 1, b = 2;
export { a, b as c };
export { d } from './d';
"""


class ScriptExportsTest(unittest.TestCase):
    def test_kinds_components_and_lists(self):
        found = {e.name: e for e in script_exports(scan_source(SOURCE), jsx=True)}
        self.assertTrue(found["Button"].component)
        self.assertTrue(found["Card"].component)
        self.assertFalse(found["Styles"].component)
        self.assertTrue(found["Store"].default and found["Store"].is_concept)
        self.assertFalse(found["Props"].is_value)
        self.assertIn("a", found)
        self.assertIn("b", found)
        self.assertNotIn("d", found)

    def test_no_components_outside_jsx(self):
        found = script_exports(scan_source("export function Button() {}\n"), jsx=False)
        self.assertFalse(found[0].component)


if __name__ == "__main__":
    unittest.main()
