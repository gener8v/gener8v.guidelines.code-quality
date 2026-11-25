import unittest

from cq_measure.fixture_repository import findings_for
from cq_measure.source.comments import python_comments
from cq_measure.suppression import parse_suppressions

LONG = "\n".join(f"x{i} = {i}" for i in range(310)) + "\n"


class SuppressionTest(unittest.TestCase):
    def test_parse(self):
        result = parse_suppressions(python_comments("a = 1\n\n\n\n\n\nb = 2  # cq-ignore nesting, params: legacy\nc = 3  # cq-ignore fan-out\n"))
        self.assertEqual(result.by_line[7], {"nesting", "params"})
        self.assertEqual(result.unexplained, [(8, "fan-out")])
        self.assertEqual(result.whole_file, set())

    def test_header_suppresses_whole_file(self):
        self.assertEqual(findings_for({"a.py": "# cq-ignore file-lines: generated table\n" + LONG}, "file-lines"), [])
        self.assertEqual(len(findings_for({"a.py": LONG}, "file-lines")), 1)

    def test_reason_is_required(self):
        found = findings_for({"a.py": "x = 1  # cq-ignore nesting\n"}, "suppression-reason")
        self.assertEqual([(f.line, f.severity, f.rule) for f in found], [(1, "warn", None)])
        self.assertEqual(findings_for({"a.py": "x = 1  # cq-ignore nesting: why\n"}, "suppression-reason"), [])


if __name__ == "__main__":
    unittest.main()
