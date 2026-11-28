import unittest

from cq_measure.testing import findings_for


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
