import unittest

from cq_measure.configuration import load_defaults
from cq_measure.structure.functions.each_function import each_function
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


class EachFunctionTest(unittest.TestCase):
    def test_leaves_out_generated_code_and_declarations(self):
        files = {
            "a.py": "def total():\n    return 1\n",
            "gen.py": "# @generated\ndef parse():\n    return 1\n",
            "env.d.ts": "declare function boot(): void;\n",
        }
        with measure(files) as workspace:
            found = [(source.path, function.name) for source, function in each_function(workspace)]
        self.assertEqual(found, [("a.py", "total")])


if __name__ == "__main__":
    unittest.main()
