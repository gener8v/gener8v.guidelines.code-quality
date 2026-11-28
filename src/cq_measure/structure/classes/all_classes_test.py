import unittest

from cq_measure.configuration import load_defaults
from cq_measure.structure.classes.all_classes import all_classes
from cq_measure.testing import fixture_repo
from cq_measure.workspace import load_workspace


def measure(files):
    """Yield a workspace for a repository made of `files`."""
    return _Repository(files)


class _Repository:
    def __init__(self, files):
        self.files = files

    def __enter__(self):
        self.context = fixture_repo(self.files)
        root = self.context.__enter__()
        return load_workspace(root, load_defaults())

    def __exit__(self, *exc):
        return self.context.__exit__(*exc)


class AllClassesTest(unittest.TestCase):
    def test_collects_classes_of_every_language_once(self):
        files = {"a.py": "class Invoice:\n    pass\n", "b.ts": "interface Port { send(): void }\n"}
        with measure(files) as workspace:
            found = all_classes(workspace)
            self.assertIs(found, all_classes(workspace))
        self.assertEqual(sorted((s.path, c.name) for s, c in found), [("a.py", "Invoice"), ("b.ts", "Port")])


if __name__ == "__main__":
    unittest.main()
