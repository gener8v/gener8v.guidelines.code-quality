import unittest

from cq_measure.testing import findings_for


class ImplNamingTest(unittest.TestCase):
    def test_marked_names(self):
        files = {"a.ts": "export interface IInvoiceStore { get(): void }\nexport class InvoiceStoreImpl {}\n"}
        self.assertEqual(len(findings_for(files, "impl-naming")), 2)
        self.assertEqual(findings_for({"a.ts": "export interface InvoiceStore {}\nexport class IOError {}\n"}, "impl-naming"), [])


if __name__ == "__main__":
    unittest.main()
