import unittest

from cq_measure.source.globs import compile_glob, matches_any


class GlobsTest(unittest.TestCase):
    def test_unanchored_patterns_match_at_any_depth(self):
        self.assertTrue(matches_any("node_modules/x/y.js", ["node_modules/**"]))
        self.assertTrue(matches_any("apps/web/node_modules/x.js", ["node_modules/**"]))
        self.assertTrue(matches_any("a/__pycache__/b.pyc", ["**/__pycache__/**"]))

    def test_anchored_and_wildcards(self):
        self.assertFalse(matches_any("src/dist/x.js", ["/dist/**"]))
        self.assertTrue(compile_glob("*.config.*").match("vite.config.ts"))
        self.assertFalse(compile_glob("*.config.*").match("src/config.ts"))
        self.assertFalse(matches_any("src/a.py", ["build/**"]))


if __name__ == "__main__":
    unittest.main()
