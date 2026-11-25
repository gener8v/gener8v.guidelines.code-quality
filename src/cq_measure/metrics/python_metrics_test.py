import ast
import unittest

from cq_measure.metrics.python_metrics import has_logic, measure_python

SOURCE = '''
def ship(order, carrier, *, fast=False, verbose: bool = False):
    """Docstring is not counted."""
    if order and order.paid or carrier:
        for item in order.items:
            while item:
                try:
                    item = item.next
                except ValueError:
                    break
    elif order:
        return [x for x in order if x]
    return None


class Box:
    def put(self, item, strict: bool):
        def inner():
            if item:
                return 1
        return inner
'''


class PythonMetricsTest(unittest.TestCase):
    def setUp(self):
        self.measures = {m.name: m for m in measure_python(ast.parse(SOURCE), SOURCE.splitlines())}

    def test_ship(self):
        ship = self.measures["ship"]
        self.assertEqual(ship.lines, 10)
        self.assertEqual(ship.nesting, 4)
        self.assertEqual(ship.complexity, 10)
        self.assertEqual(ship.params, 4)
        self.assertEqual(ship.flag_params, ())

    def test_method_excludes_self_and_nested_scopes(self):
        put = self.measures["put"]
        self.assertEqual(put.params, 2)
        self.assertEqual(put.flag_params, ("strict",))
        self.assertEqual(put.complexity, 1)
        self.assertEqual(self.measures["inner"].complexity, 2)

    def test_has_logic(self):
        self.assertTrue(has_logic(ast.parse(SOURCE)))
        self.assertFalse(has_logic(ast.parse("class P:\n    def f(self):\n        ...\nX = 1\n")))


if __name__ == "__main__":
    unittest.main()
