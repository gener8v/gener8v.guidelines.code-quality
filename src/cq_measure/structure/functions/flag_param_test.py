import unittest

from cq_measure.testing import findings_for


class FlagParamTest(unittest.TestCase):
    def test_positional_booleans(self):
        source = "def export(report, as_pdf: bool):\n    pass\n\n\ndef render(page, compact=False):\n    pass\n"
        self.assertEqual([f.line for f in findings_for({"a.py": source}, "flag-param")], [1, 5])

    def test_keyword_only_and_dunder(self):
        source = (
            "def export(report, *, as_pdf: bool = False):\n    pass\n\n\nclass A:\n    def __init__(self, on=True):\n        pass\n\n\n"
            "@app.get('/x')\ndef endpoint(full: bool = False):\n    pass\n"
        )
        self.assertEqual(findings_for({"a.py": source}, "flag-param"), [])


if __name__ == "__main__":
    unittest.main()
