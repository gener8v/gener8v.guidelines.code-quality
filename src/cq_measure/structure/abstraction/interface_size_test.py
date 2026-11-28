import unittest

from cq_measure.testing import findings_for


class InterfaceSizeTest(unittest.TestCase):
    def test_method_counts(self):
        members = "".join(f"  m{i}(): void;\n" for i in range(8))
        self.assertEqual([f.severity for f in findings_for({"a.ts": f"interface Big {{\n{members}}}\n"}, "interface-size")], ["warn"])
        self.assertEqual(findings_for({"a.ts": "interface Props {\n  a: string;\n  onClick: () => void;\n}\n"}, "interface-size"), [])


if __name__ == "__main__":
    unittest.main()
