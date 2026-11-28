import unittest

from cq_measure.testing import findings_for


class ComplexityTest(unittest.TestCase):
    def test_branches(self):
        source = "def f(a):\n" + "".join(f"    if a == {i}:\n        return {i}\n" for i in range(11))
        self.assertEqual([f.severity for f in findings_for({"a.py": source}, "complexity")], ["warn"])
        self.assertEqual(findings_for({"a.py": "def f(a):\n    return a or 1\n"}, "complexity"), [])


if __name__ == "__main__":
    unittest.main()
