import unittest

from cq_measure.configuration import load_defaults
from cq_measure.structure.classes import all_classes
from cq_measure.testing import fixture_repo
from cq_measure.workspace import load_workspace

FILES = {
    "pkg/a.py": "class A:\n    def f(self):\n        return 1\n",
    "pkg/broken.py": "def (:\n",
    "web/b.ts": "export class B { g() { return 2; } } // note\n",
    "README.md": "A B",
}


class WorkspaceTest(unittest.TestCase):
    def test_facts_per_file(self):
        with fixture_repo(FILES) as root:
            workspace = load_workspace(root, load_defaults())
            python, broken, script = (workspace.by_path[p] for p in ("pkg/a.py", "pkg/broken.py", "web/b.ts"))
            self.assertEqual([s.path for s in workspace.sources], ["pkg/a.py", "pkg/broken.py", "web/b.ts"])
            self.assertIsNone(workspace.python_tree(broken))
            self.assertEqual([f.name for f in workspace.functions(python)], ["f"])
            self.assertEqual([c.text for c in workspace.comments(script)], ["note"])
            self.assertEqual([e.name for e in workspace.exports(script)], ["B"])
            self.assertEqual(sorted(info.name for _s, info in all_classes(workspace)), ["A", "B"])
            self.assertEqual(workspace.mentions["B"], 2)
            self.assertIn("pkg", workspace.directories)
            self.assertFalse(workspace.generated(python))


if __name__ == "__main__":
    unittest.main()
