import unittest

from cq_measure.testing import findings_for

LOGIC = "def total(items):\n    return sum(items)\n"


class UntestedFileTest(unittest.TestCase):
    def test_logic_without_test(self):
        found = findings_for({"src/billing.py": LOGIC, "src/cart.ts": "export function add(a, b) { return a + b; }\n"}, "untested-file")
        self.assertEqual(sorted(f.path for f in found), ["src/billing.py", "src/cart.ts"])
        self.assertIn("billing_test.py", found[0].message)

    def test_tested_or_declaration_only(self):
        files = {
            "src/billing.py": LOGIC, "src/test_billing.py": "",
            "src/types.ts": "export interface A { a: string }\nexport type F = (x: number) => void;\n",
            "src/models.py": "from dataclasses import dataclass\n\n\n@dataclass\nclass A:\n    x: int\n",
            "src/__init__.py": LOGIC,
            "src/vite.config.ts": "export default { plugins: [() => 1] };\n",
        }
        self.assertEqual(findings_for(files, "untested-file"), [])


if __name__ == "__main__":
    unittest.main()
