import json
import unittest

from cq_measure.reporting.findings import Finding
from cq_measure.reporting.output import render_json, render_text, summarize

FINDINGS = [
    Finding("src/a.py", None, "1.1", "file-lines", "fail", "612 non-blank lines; fail above 500. Split it."),
    Finding("src/a.py", 4, None, "suppression-reason", "warn", "No reason."),
]


class OutputTest(unittest.TestCase):
    def test_text(self):
        text = render_text(FINDINGS, summarize(FINDINGS, 3))
        self.assertIn("src/a.py  1.1  file-lines  fail  612 non-blank lines", text)
        self.assertIn("src/a.py:4  -  suppression-reason  warn", text)
        self.assertIn("3 files measured: 1 fail, 1 warn.", text)

    def test_json(self):
        data = json.loads(render_json(FINDINGS, summarize(FINDINGS, 3)))
        self.assertEqual(data["findings"][0]["check"], "file-lines")
        self.assertEqual(data["summary"]["by_check"]["file-lines"], {"fail": 1})


if __name__ == "__main__":
    unittest.main()
