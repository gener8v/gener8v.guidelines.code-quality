import unittest

from cq_measure.testing import findings_for


class FileNameCaseTest(unittest.TestCase):
    def test_wrong_cases(self):
        files = {"src/userProfile.ts": "", "src/BadName.py": "", "src/order_list.ts": ""}
        found = findings_for(files, "file-name-case")
        self.assertEqual(sorted(f.path for f in found), ["src/BadName.py", "src/order_list.ts", "src/userProfile.ts"])

    def test_conventions_and_exemptions(self):
        files = {
            "src/user.service.ts": "", "src/user-profile.test.ts": "", "src/__init__.py": "", "src/_private.py": "",
            "src/test_invoice.py": "", "app/[id]/page.tsx": "", "src/Button.tsx": "", "src/Card.tsx": "",
            "src/vite-env.d.ts": "", "Invoice.java": "",
        }
        self.assertEqual(findings_for(files, "file-name-case"), [])

    def test_tsx_follows_the_repository_majority(self):
        files = {"a/Button.tsx": "", "a/Card.tsx": "", "a/date-picker.tsx": ""}
        self.assertEqual([f.path for f in findings_for(files, "file-name-case")], ["a/date-picker.tsx"])


if __name__ == "__main__":
    unittest.main()
