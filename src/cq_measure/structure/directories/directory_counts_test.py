import unittest

from cq_measure.configuration import load_defaults
from cq_measure.structure.directories.directory_counts import measured_directories
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


class MeasuredDirectoriesTest(unittest.TestCase):
    def test_leaves_out_hidden_and_generated_directories(self):
        files = {"src/billing/a.py": "", ".github/workflows/ci.yml": "", "src/generated/api.ts": ""}
        with measure(files) as workspace:
            paths = [path for path, _ in measured_directories(workspace)]
        self.assertEqual(paths, ["", "src", "src/billing"])


if __name__ == "__main__":
    unittest.main()
