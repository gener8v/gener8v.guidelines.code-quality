import unittest

from cq_measure.codebase.directory_tree import build_directories, has_hidden_part


class DirectoryTest(unittest.TestCase):
    def test_builds_tree_from_paths(self):
        tree = build_directories(["README.md", "src/app/main.py", "src/app/views/home.py"])
        self.assertEqual(tree[""].files, ["README.md"])
        self.assertEqual(tree[""].subdirs, {"src"})
        self.assertEqual(tree["src"].subdirs, {"app"})
        self.assertEqual(tree["src/app"].files, ["main.py"])
        self.assertEqual(tree["src/app/views"].name, "views")

    def test_hidden_parts(self):
        self.assertTrue(has_hidden_part(".github/workflows"))
        self.assertFalse(has_hidden_part("src/app"))


if __name__ == "__main__":
    unittest.main()
