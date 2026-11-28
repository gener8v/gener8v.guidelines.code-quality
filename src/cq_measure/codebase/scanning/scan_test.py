import unittest

from cq_measure.codebase.scanning.scan import Scan


class ScanTest(unittest.TestCase):
    def test_line_of_offset(self):
        scan = Scan("ab\ncd\n", line_starts=[0, 3, 6])
        self.assertEqual(scan.line_of(0), 1)
        self.assertEqual(scan.line_of(3), 2)
        self.assertEqual(scan.line_of(4), 2)


if __name__ == "__main__":
    unittest.main()
