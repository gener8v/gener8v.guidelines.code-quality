import unittest

from cq_measure.testing import findings_for


class TestNameTest(unittest.TestCase):
    def test_test_without_subject(self):
        found = findings_for({"src/helpers.test.ts": "", "src/a.ts": ""}, "test-name")
        self.assertEqual([f.path for f in found], ["src/helpers.test.ts"])

    def test_named_for_subject_or_package(self):
        files = {"src/a.ts": "", "src/a.test.ts": "", "src/billing/x.py": "", "src/test_billing.py": ""}
        self.assertEqual(findings_for(files, "test-name"), [])


if __name__ == "__main__":
    unittest.main()
