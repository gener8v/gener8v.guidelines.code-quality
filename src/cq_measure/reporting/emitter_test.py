import unittest

from cq_measure.reporting.emitter import Emitter

SPEC = {"rule": "1.1", "warn": 300, "fail": 500, "test_warn": 500, "test_fail": 800}


class EmitterTest(unittest.TestCase):
    def test_grades_against_thresholds(self):
        emitter = Emitter("file-lines", SPEC)
        emitter.measure(("a.py", None), 612, ("612 lines", "Split it."))
        emitter.measure(("b.py", None), 301, ("301 lines", "Split it."))
        emitter.measure(("c.py", None), 300, ("300 lines", "Split it."))
        emitter.measure(("d_test.py", None), 612, ("612 lines", "Split it."), test=True)
        self.assertEqual([(f.path, f.severity) for f in emitter.findings], [("a.py", "fail"), ("b.py", "warn"), ("d_test.py", "warn")])
        self.assertEqual(emitter.findings[0].message, "612 lines; fail above 500. Split it.")

    def test_flag_uses_fixed_severity(self):
        emitter = Emitter("deep-import", {"rule": "3.2", "severity": "fail"})
        emitter.flag(("a.ts", 3), "Bad.")
        self.assertEqual((emitter.findings[0].severity, emitter.findings[0].rule), ("fail", "3.2"))
        self.assertEqual(emitter.option("missing", 7), 7)


if __name__ == "__main__":
    unittest.main()
