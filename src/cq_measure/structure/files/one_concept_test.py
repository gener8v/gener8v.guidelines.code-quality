import unittest

from cq_measure.testing import findings_for

MODELS = "class Invoice:\n    pass\n\n\nclass Customer:\n    pass\n\n\nclass BillingError(Exception):\n    pass\n"


class OneConceptTest(unittest.TestCase):
    def test_two_public_classes(self):
        found = findings_for({"models.py": MODELS}, "one-concept")
        self.assertEqual([(f.path, f.line) for f in found], [("models.py", 5)])

    def test_one_class_with_private_helper_and_error(self):
        source = "class Invoice:\n    pass\n\n\nclass _Line:\n    pass\n\n\nclass InvoiceError(Exception):\n    pass\n"
        self.assertEqual(findings_for({"invoice.py": source}, "one-concept"), [])

    def test_components_in_tsx(self):
        source = "export function Header() { return null; }\nexport const Footer = () => null;\nexport const theme = {};\n"
        self.assertEqual(len(findings_for({"page-frame.tsx": source}, "one-concept")), 1)
        self.assertEqual(findings_for({"header.tsx": "export function Header() { return null; }\n"}, "one-concept"), [])


if __name__ == "__main__":
    unittest.main()
