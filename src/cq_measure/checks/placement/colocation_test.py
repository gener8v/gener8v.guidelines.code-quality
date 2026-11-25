import unittest

from cq_measure.fixture_repository import findings_for


class TestColocationTest(unittest.TestCase):
    def test_test_in_another_directory(self):
        files = {"src/billing/invoice.py": "", "tests/billing/test_invoice.py": "from billing.invoice import total\n"}
        found = findings_for(files, "test-colocation")
        self.assertEqual([(f.path, f.severity) for f in found], [("tests/billing/test_invoice.py", "fail")])

    def test_same_name_elsewhere_but_not_imported(self):
        files = {"server/config.ts": "", "web/config.test.ts": "import { x } from './settings';\n", "web/settings.ts": ""}
        self.assertEqual(findings_for(files, "test-colocation"), [])
        self.assertEqual([f.path for f in findings_for(files, "test-name")], ["web/config.test.ts"])

    def test_colocated_and_cross_cutting(self):
        files = {
            "src/invoice.py": "", "src/invoice_test.py": "",
            "web/Button.tsx": "", "web/__tests__/button.test.tsx": "",
            "tests/e2e/test_invoice.py": "",
            "src/main/java/a/Invoice.java": "", "src/test/java/a/InvoiceTest.java": "",
        }
        self.assertEqual(findings_for(files, "test-colocation"), [])


class TestNameTest(unittest.TestCase):
    def test_test_without_subject(self):
        found = findings_for({"src/helpers.test.ts": "", "src/a.ts": ""}, "test-name")
        self.assertEqual([f.path for f in found], ["src/helpers.test.ts"])

    def test_named_for_subject_or_package(self):
        files = {"src/a.ts": "", "src/a.test.ts": "", "src/billing/x.py": "", "src/test_billing.py": ""}
        self.assertEqual(findings_for(files, "test-name"), [])


if __name__ == "__main__":
    unittest.main()
