import unittest

from cq_measure.testing import findings_for


class DirNameCaseTest(unittest.TestCase):
    def test_bad_directory_names(self):
        files = {"src/BillingStuff/a.ts": "", "src/my-pkg/a.py": "", "src/user_profile/a.ts": ""}
        found = findings_for(files, "dir-name-case")
        self.assertEqual(sorted(f.path for f in found), ["src/BillingStuff", "src/my-pkg", "src/user_profile"])

    def test_case_follows_the_language(self):
        files = {
            "src/Ordering.Domain/Order.cs": "", "src/ordering-api/Api.cs": "",
            "com/acme/customer/A.java": "", "com/acme/order_lines/B.java": "",
            "internal/userstore/s.go": "", "internal/user-store/s.go": "",
        }
        found = sorted(f.path for f in findings_for(files, "dir-name-case"))
        self.assertEqual(found, ["com/acme/order_lines", "internal/user-store", "src/ordering-api"])

    def test_allowed_names(self):
        files = {"src/my_pkg/a.py": "", "src/user-profile/a.ts": "", "src/__tests__/a.test.ts": "", "app/[id]/page.tsx": "", "app/(auth)/x.tsx": ""}
        self.assertEqual(findings_for(files, "dir-name-case"), [])


if __name__ == "__main__":
    unittest.main()
