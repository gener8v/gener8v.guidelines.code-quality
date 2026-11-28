import unittest

from cq_measure.testing import findings_for


class LayerDirectionTest(unittest.TestCase):
    def test_inner_imports_outer(self):
        files = {"src/domain/order.py": "from src.db import session\n", "src/db/session.py": "", "src/__init__.py": ""}
        found = findings_for(files, "layer-direction")
        self.assertEqual([f.path for f in found], ["src/domain/order.py"])

    def test_outer_imports_inner_and_shared_prefix(self):
        files = {
            "src/db/repo.py": "from src.domain import order\n",
            "src/domain/order.py": "",
            "api/models/user.py": "from api import routes\n",
            "api/routes.py": "",
        }
        self.assertEqual(findings_for(files, "layer-direction"), [])


if __name__ == "__main__":
    unittest.main()
