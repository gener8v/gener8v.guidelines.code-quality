import unittest

from cq_measure.testing import findings_for


class ClassMethodsTest(unittest.TestCase):
    def test_method_counts(self):
        methods = "".join(f"    def m{i}(self):\n        return {i}\n" for i in range(16))
        self.assertEqual([f.severity for f in findings_for({"a.py": f"class Big:\n{methods}"}, "class-methods")], ["warn"])
        self.assertEqual(findings_for({"a.py": "class Small:\n    def m(self):\n        return 1\n"}, "class-methods"), [])


if __name__ == "__main__":
    unittest.main()
