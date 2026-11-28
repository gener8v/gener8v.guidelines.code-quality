import unittest

from cq_measure.codebase.package_roots import (
    is_within,
    nearest_root,
    package_roots,
    parts_of,
)


class PackagesTest(unittest.TestCase):
    def test_roots_from_manifests(self):
        roots = package_roots(["package.json", "apps/web/package.json", "svc/pyproject.toml", "x/readme.md"])
        self.assertEqual(roots, {"", "apps/web", "svc"})

    def test_nearest_root_and_parts(self):
        self.assertEqual(nearest_root("apps/web/src/ui", {"", "apps/web"}), "apps/web")
        self.assertEqual(nearest_root("lib/x", {"", "apps/web"}), "")
        self.assertEqual(parts_of(""), [])
        self.assertEqual(parts_of("a/b"), ["a", "b"])

    def test_is_within(self):
        self.assertTrue(is_within("a/b/c.py", "a/b"))
        self.assertTrue(is_within("a/b/c.py", ""))
        self.assertFalse(is_within("a/bc/c.py", "a/b"))


if __name__ == "__main__":
    unittest.main()
