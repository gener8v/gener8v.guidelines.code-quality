import unittest

from cq_measure.fixture_repository import findings_for


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


class ClassMethodsTest(unittest.TestCase):
    def test_method_counts(self):
        methods = "".join(f"    def m{i}(self):\n        return {i}\n" for i in range(16))
        self.assertEqual([f.severity for f in findings_for({"a.py": f"class Big:\n{methods}"}, "class-methods")], ["warn"])
        self.assertEqual(findings_for({"a.py": "class Small:\n    def m(self):\n        return 1\n"}, "class-methods"), [])


if __name__ == "__main__":
    unittest.main()
