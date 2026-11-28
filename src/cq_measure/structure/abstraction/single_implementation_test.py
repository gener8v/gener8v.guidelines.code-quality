import unittest

from cq_measure.testing import findings_for

STORE = "from abc import ABC, abstractmethod\n\n\nclass Store(ABC):\n    @abstractmethod\n    def get(self, key):\n        ...\n"


class SingleImplementationTest(unittest.TestCase):
    def test_one_implementation(self):
        files = {"store.py": STORE, "pg.py": "from store import Store\n\n\nclass PgStore(Store):\n    pass\n"}
        found = findings_for(files, "single-implementation")
        self.assertEqual([(f.path, f.line) for f in found], [("store.py", 4)])

    def test_fake_counts_as_second(self):
        files = {
            "store.py": STORE,
            "pg.py": "class PgStore(Store):\n    pass\n",
            "store_test.py": "class FakeStore(Store):\n    pass\n",
            "port.ts": "export interface Clock { now(): number }\nclass Sys implements Clock { now() { return 1; } }\nconst fake: Clock = { now: () => 2 };\n",
        }
        self.assertEqual(findings_for(files, "single-implementation"), [])


if __name__ == "__main__":
    unittest.main()
