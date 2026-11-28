import unittest

from cq_measure.testing import findings_for


def _lines(count):
    return "".join(f"x{i} = {i}\n" for i in range(count))


class FileLinesTest(unittest.TestCase):
    def test_source_thresholds(self):
        found = findings_for({"a.py": _lines(501), "b.py": _lines(301), "c.py": _lines(300) + "\n\n"}, "file-lines")
        self.assertEqual([(f.path, f.severity) for f in found], [("a.py", "fail"), ("b.py", "warn")])
        self.assertIn("501 non-blank lines; fail above 500.", found[0].message)

    def test_test_file_thresholds(self):
        found = findings_for({"a_test.py": _lines(501), "b_test.py": _lines(801)}, "file-lines")
        self.assertEqual([(f.path, f.severity) for f in found], [("a_test.py", "warn"), ("b_test.py", "fail")])


if __name__ == "__main__":
    unittest.main()
