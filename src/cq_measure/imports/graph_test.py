import unittest

from cq_measure.fixture_repository import fixture_repo
from cq_measure.config import load_defaults
from cq_measure.imports.graph import strongly_connected
from cq_measure.workspace import load_workspace


class GraphTest(unittest.TestCase):
    def test_builds_edges_for_python_and_typescript(self):
        files = {
            "pkg/a.py": "from pkg import b\nimport json\n",
            "pkg/b.py": "",
            "pkg/__init__.py": "",
            "web/x.ts": "import { y } from './y';\nimport type { Z } from './z';\n",
            "web/y.ts": "export const y = 1;\n",
            "web/z.ts": "export type Z = 1;\n",
        }
        with fixture_repo(files) as root:
            graph = load_workspace(root, load_defaults()).graph
        self.assertEqual(set(graph.edges["pkg/a.py"]), {"pkg/b.py"})
        self.assertEqual(set(graph.edges["web/x.ts"]), {"web/y.ts", "web/z.ts"})
        self.assertTrue(graph.edges["web/x.ts"]["web/z.ts"].type_only)
        self.assertEqual(graph.importers["web/y.ts"], {"web/x.ts"})

    def test_strongly_connected(self):
        graph = {"a": ["b"], "b": ["c"], "c": ["a"], "d": ["a"]}
        components = strongly_connected(graph)
        self.assertIn(["a", "b", "c"], components)
        self.assertIn(["d"], components)


if __name__ == "__main__":
    unittest.main()
