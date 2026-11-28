import unittest

from cq_measure.codebase import scan_source
from cq_measure.structure.functions.approximation.javascript_metrics import (
    measure_javascript,
)

SOURCE = """function route(req, res) {
  if (req.a && req.b) {
    for (const x of req.items) {
      try {
        if (x) { send(x); } else { skip(x ?? 0); }
      } catch (e) {
        res.fail(e ? 1 : 2);
      }
    }
  }
  const inner = () => { if (a || b) { return 1; } };
  switch (req.kind) { case 1: break; case 2: break; }
}
"""


class JavaScriptMetricsTest(unittest.TestCase):
    def setUp(self):
        self.measures = {m.name: m for m in measure_javascript(scan_source(SOURCE), SOURCE.splitlines())}

    def test_outer_function(self):
        route = self.measures["route"]
        self.assertEqual(route.lines, 11)
        self.assertEqual(route.nesting, 4)
        self.assertEqual(route.complexity, 10)
        self.assertEqual(route.params, 2)

    def test_nested_function_is_measured_alone(self):
        inner = self.measures["inner"]
        self.assertEqual(inner.complexity, 3)
        self.assertEqual(inner.nesting, 1)


if __name__ == "__main__":
    unittest.main()
