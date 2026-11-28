import unittest

from cq_measure.configuration import load_defaults
from cq_measure.structure.test_placement.subjects import (
    misplaced_tests,
    subject_dirs,
    subject_index,
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


class SubjectsTest(unittest.TestCase):
    def test_index_holds_sources_and_test_support_but_not_tests(self):
        files = {"billing/invoice.py": "", "billing/invoice_test.py": "", "testing/fixture_repository.py": ""}
        with measure(files) as workspace:
            index = subject_index(workspace)
        self.assertEqual(index[("python", "invoice")], ["billing/invoice.py"])
        self.assertEqual(index[("python", "fixturerepository")], ["testing/fixture_repository.py"])

    def test_subject_directories(self):
        self.assertEqual(subject_dirs("src/__tests__/a.test.ts"), ["src/__tests__", "src"])
        self.assertEqual(subject_dirs("app/src/test/java/A.java"), ["app/src/test/java", "app/src/main/java"])

    def test_misplaced_tests_name_the_subject_that_they_import(self):
        files = {
            "billing/__init__.py": "",
            "billing/invoice.py": "",
            "billing/order.py": "",
            "billing/order_test.py": "",
            "tests/billing/invoice_test.py": "from billing.invoice import total\n",
            "tests/billing/refund_test.py": "",
        }
        with measure(files) as workspace:
            found = [(test.path, subject, paths) for test, subject, paths in misplaced_tests(workspace, subject_index(workspace))]
        self.assertEqual(found, [("tests/billing/invoice_test.py", "invoice", ["billing/invoice.py"]), ("tests/billing/refund_test.py", "refund", [])])


if __name__ == "__main__":
    unittest.main()
