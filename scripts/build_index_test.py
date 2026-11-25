import tempfile
import unittest
from pathlib import Path

import build_index


class ParseMeasureTest(unittest.TestCase):
    def test_reads_thresholds_and_test_thresholds(self):
        text = "`file-lines` — warn above 300, fail above 500. Test files: warn above 500, fail above 800."
        (check,) = build_index.parse_measure(text)
        self.assertEqual(("file-lines", "threshold", 300, 500, 500, 800),
                         (check.check_id, check.severity, check.warn, check.fail, check.test_warn, check.test_fail))

    def test_reads_two_severity_checks(self):
        checks = build_index.parse_measure("`root-files` — warn. `root-source` — fail.")
        self.assertEqual([("root-files", "warn"), ("root-source", "fail")],
                         [(c.check_id, c.severity) for c in checks])

    def test_judged_rule_has_no_checks(self):
        self.assertEqual([], build_index.parse_measure("judged (self-check)."))


class ParseSectionTest(unittest.TestCase):
    def write(self, text):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path = Path(directory.name) / "01-files.md"
        path.write_text(text, encoding="utf-8")
        return path

    def test_reports_a_rule_number_out_of_order(self):
        path = self.write("# 1. Files\n\n### 1.2 Skip\n\n**Measure:** judged.\n")
        errors = []
        build_index.parse_section(path, errors)
        self.assertIn("rule 1.2 must be 1.1", errors[0])

    def test_reports_a_rule_with_no_measure(self):
        path = self.write("# 1. Files\n\n### 1.1 Keep files short\n\nText.\n")
        errors = []
        build_index.parse_section(path, errors)
        self.assertIn("has no **Measure:** line", errors[0])


class CompareDefaultsTest(unittest.TestCase):
    def parts_with(self, measure):
        rule = build_index.Rule("1.1", "Keep files short", measure, build_index.parse_measure(measure))
        section = build_index.Section(1, "Files", Path("01-files.md"), [rule])
        return [("Part A", [section])]

    def test_accepts_matching_defaults(self):
        errors = []
        defaults = {"checks": {"file-lines": {"rule": "1.1", "warn": 300, "fail": 500}}}
        build_index.compare_defaults(self.parts_with("`file-lines` — warn above 300, fail above 500."), defaults, errors)
        self.assertEqual([], errors)

    def test_reports_a_threshold_mismatch(self):
        errors = []
        defaults = {"checks": {"file-lines": {"rule": "1.1", "warn": 400, "fail": 500}}}
        build_index.compare_defaults(self.parts_with("`file-lines` — warn above 300, fail above 500."), defaults, errors)
        self.assertIn("warn is 300 in the guideline, 400 in defaults.json", errors[0])

    def test_reports_a_check_that_no_guideline_names(self):
        errors = []
        defaults = {"checks": {"orphan-file": {"rule": "7.2", "severity": "warn"}}}
        build_index.compare_defaults(self.parts_with("judged."), defaults, errors)
        self.assertIn("is not named in any guideline", errors[0])

    def test_ignores_a_check_with_no_rule(self):
        errors = []
        defaults = {"checks": {"suppression-reason": {"rule": None, "severity": "warn"}}}
        build_index.compare_defaults(self.parts_with("judged."), defaults, errors)
        self.assertEqual([], errors)


if __name__ == "__main__":
    unittest.main()
