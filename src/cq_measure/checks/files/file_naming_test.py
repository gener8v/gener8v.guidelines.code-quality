import unittest

from cq_measure.fixture_repository import findings_for


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


class RoleSuffixTest(unittest.TestCase):
    def test_mixed_separators_and_abbreviations(self):
        files = {"a/user.service.ts": "", "a/order.service.ts": "", "a/payment-service.ts": "", "a/cart-svc.ts": ""}
        found = findings_for(files, "role-suffix")
        self.assertEqual(sorted(f.path for f in found), ["a/cart-svc.ts", "a/payment-service.ts"])

    def test_one_spelling(self):
        files = {"a/user.service.ts": "", "a/order.service.ts": "", "b/user_service.py": "", "b/repo.py": ""}
        self.assertEqual(findings_for(files, "role-suffix"), [])


if __name__ == "__main__":
    unittest.main()
