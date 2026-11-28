import unittest

from cq_measure.testing import findings_for


class NameMatchesExportTest(unittest.TestCase):
    def test_mismatch(self):
        found = findings_for({"billing.py": "class InvoiceService:\n    pass\n"}, "name-matches-export")
        self.assertEqual(len(found), 1)
        self.assertIn("invoice_service.py", found[0].message)

    def test_matches_ignoring_case_and_separators(self):
        files = {
            "invoice_service.py": "class InvoiceService:\n    pass\n",
            "invoice-list.tsx": "export function InvoiceList() { return null; }\n",
            "user.service.ts": "export class UserService {}\n",
            "button/index.tsx": "export function Button() { return null; }\n",
            "parser.py": "class Result:\n    pass\n\n\ndef parse():\n    pass\n",
        }
        self.assertEqual(findings_for(files, "name-matches-export"), [])


if __name__ == "__main__":
    unittest.main()
