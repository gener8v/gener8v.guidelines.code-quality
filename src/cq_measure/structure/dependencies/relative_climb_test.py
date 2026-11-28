import unittest

from cq_measure.testing import findings_for


class RelativeClimbTest(unittest.TestCase):
    def test_climbs(self):
        files = {
            "a/b/c/d/x.ts": "import y from '../../../y';\nimport z from '../../../../z';\nimport w from '../../w';\n",
            "p/q/r.py": "from ... import s\n",
        }
        found = findings_for(files, "relative-climb")
        self.assertEqual([(f.path, f.line, f.severity) for f in found], [("a/b/c/d/x.ts", 1, "warn"), ("a/b/c/d/x.ts", 2, "fail")])


if __name__ == "__main__":
    unittest.main()
