import unittest

from cq_measure.testing import findings_for


class NestingTest(unittest.TestCase):
    def test_deep_blocks(self):
        source = "def f(a):\n    if a:\n        for b in a:\n            while b:\n                if b:\n                    return 1\n"
        self.assertEqual([f.severity for f in findings_for({"a.py": source}, "nesting")], ["warn"])
        self.assertEqual(findings_for({"a.py": "def f(a):\n    if a:\n        return 1\n"}, "nesting"), [])


if __name__ == "__main__":
    unittest.main()
