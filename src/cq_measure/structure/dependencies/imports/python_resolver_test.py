import unittest

from cq_measure.structure.dependencies.imports.python_imports import PythonImport
from cq_measure.structure.dependencies.imports.python_resolver import PythonResolver

KNOWN = {
    "src/shop/__init__.py",
    "src/shop/billing/__init__.py",
    "src/shop/billing/invoice.py",
    "src/shop/cart.py",
}


class PythonResolverTest(unittest.TestCase):
    def setUp(self):
        self.resolver = PythonResolver(KNOWN, {""})

    def test_absolute_import_through_src(self):
        records = self.resolver.resolve("src/shop/cart.py", PythonImport(1, "shop.billing.invoice", 0, (), False))
        self.assertEqual([r.target for r in records], ["src/shop/billing/invoice.py"])

    def test_from_import_of_submodule_and_name(self):
        statement = PythonImport(2, "shop.billing", 0, ("invoice", "total"), False)
        records = self.resolver.resolve("src/shop/cart.py", statement)
        self.assertEqual({(r.target, r.names) for r in records}, {("src/shop/billing/invoice.py", ()), ("src/shop/billing/__init__.py", ("total",))})

    def test_relative_import_and_climb(self):
        records = self.resolver.resolve("src/shop/billing/invoice.py", PythonImport(3, "cart", 2, ("Cart",), False))
        self.assertEqual(records[0].target, "src/shop/cart.py")
        self.assertEqual((records[0].climb, records[0].specifier), (1, "..cart"))

    def test_external_import_is_unresolved(self):
        records = self.resolver.resolve("src/shop/cart.py", PythonImport(4, "requests", 0, (), False))
        self.assertEqual([r.target for r in records], [None])


if __name__ == "__main__":
    unittest.main()
