import unittest

from cq_measure.testing import findings_for

BLOCK = "".join(f"    total_{i} = compute_value(order.items[{i}], rate={i})\n" for i in range(9))


class DuplicateBlockTest(unittest.TestCase):
    def test_repeated_block(self):
        files = {"a.py": f"def f(order):\n{BLOCK}", "b.py": f"import os\n\n\ndef g(order):\n{BLOCK}"}
        found = findings_for(files, "duplicate-block")
        self.assertEqual([(f.path, f.line) for f in found], [("b.py", 5)])
        self.assertIn("9 lines repeat `a.py:2`", found[0].message)

    def test_short_or_test_copies(self):
        short = "".join(f"    x{i} = {i}\n" for i in range(9))
        files = {"a.py": f"def f():\n{short}", "b.py": f"def g():\n{short}", "a_test.py": BLOCK, "b_test.py": BLOCK}
        self.assertEqual(findings_for(files, "duplicate-block"), [])


if __name__ == "__main__":
    unittest.main()
