import unittest

from cq_measure.testing import findings_for


class ParamsTest(unittest.TestCase):
    def test_parameter_counts(self):
        source = "def f(a, b, c, d, e):\n    pass\n\n\nclass K:\n    def g(self, a, b, c, d):\n        pass\n"
        found = findings_for({"a.py": source}, "params")
        self.assertEqual([(f.line, f.severity) for f in found], [(1, "warn")])
        self.assertEqual([f.severity for f in findings_for({"a.ts": "function f(a, b, c, d, e, f, g) {}\n"}, "params")], ["fail"])


if __name__ == "__main__":
    unittest.main()
