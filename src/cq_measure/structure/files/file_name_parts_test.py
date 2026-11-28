import unittest

from cq_measure.codebase import SourceFile
from cq_measure.structure.files.file_name_parts import core_name
from cq_measure.testing import fixture_repo


class CoreNameTest(unittest.TestCase):
    def test_drops_test_markers(self):
        files = {"invoice_test.py": "", "test_order.py": "", "cart.test.ts": "", "invoice.py": ""}
        with fixture_repo(files) as root:
            names = [core_name(SourceFile(root, path)) for path in files]
        self.assertEqual(names, ["invoice", "order", "cart", "invoice"])


if __name__ == "__main__":
    unittest.main()
