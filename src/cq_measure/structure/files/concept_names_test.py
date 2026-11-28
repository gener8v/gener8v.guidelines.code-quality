import unittest

from cq_measure.configuration import load_defaults
from cq_measure.structure.files.concept_names import (
    concepts_of,
    holds_concepts,
    normalize,
)
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


class ConceptNamesTest(unittest.TestCase):
    def test_python_concepts_leave_out_exceptions_and_private_names(self):
        text = "class Invoice:\n    pass\nclass InvoiceError(Exception):\n    pass\ndef total():\n    pass\ndef _cache():\n    pass\n"
        with measure({"invoice.py": text}) as workspace:
            concepts, values = concepts_of(workspace, workspace.by_path["invoice.py"])
        self.assertEqual(([name for name, _, _ in concepts], values), (["Invoice"], 3))

    def test_tests_stories_and_framework_files_hold_no_concepts(self):
        files = {"a.py": "", "a_test.py": "", "card.stories.tsx": "", "app/page.tsx": ""}
        with measure(files) as workspace:
            holding = [path for path in files if holds_concepts(workspace, workspace.by_path[path])]
        self.assertEqual(holding, ["a.py"])

    def test_normalize_ignores_case_and_separators(self):
        self.assertEqual(normalize("invoice_service"), normalize("InvoiceService"))
        self.assertEqual(normalize("invoice-list.v2"), "invoicelistv2")


if __name__ == "__main__":
    unittest.main()
