import unittest

from cq_measure.fixture_repository import findings_for

MARK = "TO" + "DO"
PY = f"""# {MARK}: handle refunds
# {MARK}(#123): handle refunds
x = 1  # FIX{"ME"} see ABC-42
# {MARK}: split this, see
# https://example.com/issues/9
# format XXX-XXXX for phone numbers
y = "# {MARK} in a string"
"""


class TodoWithoutIssueTest(unittest.TestCase):
    def test_markers(self):
        found = findings_for({"a.py": PY}, "todo-without-issue")
        self.assertEqual([(f.line, f.severity) for f in found], [(1, "warn")])

    def test_typescript_block_comment(self):
        found = findings_for({"a.ts": f"/* HACK work around the bug */\n// {MARK} #77 done\n"}, "todo-without-issue")
        self.assertEqual([f.line for f in found], [1])


if __name__ == "__main__":
    unittest.main()
