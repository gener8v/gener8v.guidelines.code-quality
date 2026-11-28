import unittest

from cq_measure.testing import findings_for


class UnusedSymbolTest(unittest.TestCase):
    def test_unused_exports_and_definitions(self):
        files = {"a.ts": "export function usedFn() {}\nexport const unusedThing = 1;\n", "b.ts": "import { usedFn } from './a';\n", "c.py": "def orphan_helper():\n    pass\n", "d.py": "def helper():\n    pass\n\n\nhelper()\n"}
        found = findings_for(files, "unused-symbol")
        self.assertEqual(sorted((f.path, f.line) for f in found), [("a.ts", 2), ("c.py", 1)])

    def test_exemptions(self):
        files = {
            "app/api/route.ts": "export async function GET() {}\n",
            "pkg/__init__.py": "def api():\n    pass\n",
            "views.py": "@app.get('/')\ndef home():\n    pass\n\n\ndef _private():\n    pass\n",
            "lib.py": "def published():\n    pass\n",
            "page.tsx": "export default function Page() {}\nexport const metadata = {};\n",
        }
        config = {"public_symbols": ["published"]}
        self.assertEqual(findings_for(files, "unused-symbol", config), [])


if __name__ == "__main__":
    unittest.main()
