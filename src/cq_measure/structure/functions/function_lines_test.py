import unittest

from cq_measure.testing import findings_for


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


if __name__ == "__main__":
    unittest.main()
