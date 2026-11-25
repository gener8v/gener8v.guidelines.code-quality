import unittest

from cq_measure.fixture_repository import findings_for


def _long_function(lines):
    return "def big():\n" + "".join(f"    x{i} = {i}\n" for i in range(lines))


class FunctionLinesTest(unittest.TestCase):
    def test_thresholds(self):
        found = findings_for({"a.py": _long_function(41), "b.py": _long_function(81), "c.py": _long_function(40)}, "function-lines")
        self.assertEqual([(f.path, f.severity) for f in found], [("a.py", "warn"), ("b.py", "fail")])

    def test_typescript(self):
        body = "".join(f"  const x{i} = {i};\n" for i in range(45))
        found = findings_for({"a.ts": f"export function big() {{\n{body}}}\n"}, "function-lines")
        self.assertEqual([(f.line, f.severity) for f in found], [(1, "warn")])


class NestingTest(unittest.TestCase):
    def test_deep_blocks(self):
        source = "def f(a):\n    if a:\n        for b in a:\n            while b:\n                if b:\n                    return 1\n"
        self.assertEqual([f.severity for f in findings_for({"a.py": source}, "nesting")], ["warn"])
        self.assertEqual(findings_for({"a.py": "def f(a):\n    if a:\n        return 1\n"}, "nesting"), [])


class ComplexityTest(unittest.TestCase):
    def test_branches(self):
        source = "def f(a):\n" + "".join(f"    if a == {i}:\n        return {i}\n" for i in range(11))
        self.assertEqual([f.severity for f in findings_for({"a.py": source}, "complexity")], ["warn"])
        self.assertEqual(findings_for({"a.py": "def f(a):\n    return a or 1\n"}, "complexity"), [])


class ParamsTest(unittest.TestCase):
    def test_parameter_counts(self):
        source = "def f(a, b, c, d, e):\n    pass\n\n\nclass K:\n    def g(self, a, b, c, d):\n        pass\n"
        found = findings_for({"a.py": source}, "params")
        self.assertEqual([(f.line, f.severity) for f in found], [(1, "warn")])
        self.assertEqual([f.severity for f in findings_for({"a.ts": "function f(a, b, c, d, e, f, g) {}\n"}, "params")], ["fail"])


if __name__ == "__main__":
    unittest.main()
