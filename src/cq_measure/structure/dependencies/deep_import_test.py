import unittest

from cq_measure.testing import findings_for


class DeepImportTest(unittest.TestCase):
    def test_typescript_past_a_barrel(self):
        files = {
            "src/billing/index.ts": "export { roundCents } from './internal/rounding';\n",
            "src/billing/internal/rounding.ts": "export const roundCents = 1;\n",
            "src/app.ts": "import { roundCents } from './billing/internal/rounding';\nimport { x } from './billing';\n",
        }
        found = findings_for(files, "deep-import")
        self.assertEqual([(f.path, f.line) for f in found], [("src/app.ts", 1)])

    def test_python_private_module_and_name(self):
        files = {
            "billing/__init__.py": "",
            "billing/_rounding.py": "def _round():\n    pass\n",
            "billing/invoice.py": "from billing._rounding import _round\n",
            "app.py": "from billing._rounding import x\nfrom billing.invoice import _helper\n",
        }
        found = findings_for(files, "deep-import")
        self.assertEqual([(f.path, f.line) for f in found], [("app.py", 1), ("app.py", 2)])

    def test_python_past_an_entry_point(self):
        files = {
            "billing/__init__.py": "from .invoice import total\n",
            "billing/invoice.py": "def total():\n    pass\n",
            "billing/refund.py": "from billing.invoice import total\n",
            "shipping/__init__.py": "__all__ = ['rate']\nfrom shipping.rates import rate\n",
            "shipping/rates.py": "def rate():\n    pass\n",
            "app.py": "from billing.invoice import total\nfrom billing import total\nfrom shipping.rates import rate\n",
        }
        found = findings_for(files, "deep-import")
        self.assertEqual([(f.path, f.line) for f in found], [("app.py", 1), ("app.py", 3)])

    def test_python_name_equal_to_its_module(self):
        files = {
            "billing/__init__.py": "from .total import total\n",
            "billing/total.py": "def total():\n    pass\n",
            "app.py": "from billing import total\n",
        }
        self.assertEqual(findings_for(files, "deep-import"), [])

    def test_python_package_without_a_declared_api(self):
        files = {"billing/__init__.py": "", "billing/invoice.py": "", "app.py": "from billing.invoice import total\n"}
        self.assertEqual(findings_for(files, "deep-import"), [])

    def test_index_that_is_not_a_barrel(self):
        files = {"src/pages/index.ts": "export default 1;\n", "src/pages/a.ts": "", "src/app.ts": "import a from './pages/a';\n"}
        self.assertEqual(findings_for(files, "deep-import"), [])


if __name__ == "__main__":
    unittest.main()
