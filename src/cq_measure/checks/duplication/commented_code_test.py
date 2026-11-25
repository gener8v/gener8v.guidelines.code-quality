import unittest

from cq_measure.checks.duplication.commented_code import looks_like_code
from cq_measure.fixture_repository import findings_for


class CommentedCodeTest(unittest.TestCase):
    def test_commented_out_block(self):
        source = "x = 1\n# y = compute(x)\n# if y:\n#     return y\nz = 2\n"
        self.assertEqual([f.line for f in findings_for({"a.py": source}, "commented-code")], [2])
        script = "// const a = load();\n// a.save();\n// }\n"
        self.assertEqual(len(findings_for({"a.ts": script}, "commented-code")), 1)

    def test_prose_and_directives(self):
        source = "# This function returns the total of the order.\n# If the order is empty, it returns zero.\n# See the billing guide for details.\n"
        self.assertEqual(findings_for({"a.py": source}, "commented-code"), [])
        self.assertFalse(looks_like_code("eslint-disable-next-line no-console"))
        self.assertFalse(looks_like_code("the value is computed when the user asks for it"))
        self.assertTrue(looks_like_code("return self.total;"))


if __name__ == "__main__":
    unittest.main()
