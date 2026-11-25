import unittest

from cq_measure.findings import Finding, severity_rank, sort_key


class FindingsTest(unittest.TestCase):
    def test_order(self):
        self.assertLess(severity_rank("warn"), severity_rank("fail"))
        self.assertLess(severity_rank("fail"), severity_rank("never"))
        first = Finding("a.py", None, "1.1", "file-lines", "warn", "m")
        second = Finding("a.py", 3, "4.1", "function-lines", "warn", "m")
        self.assertLess(sort_key(first), sort_key(second))
        self.assertEqual(first.to_dict()["line"], None)


if __name__ == "__main__":
    unittest.main()
