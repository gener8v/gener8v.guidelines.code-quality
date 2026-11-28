import unittest

from cq_measure.codebase import scan_source
from cq_measure.structure.functions.approximation.javascript_functions import (
    count_params,
    find_functions,
    match_brackets,
    type_spans,
)

SOURCE = """export function load<T>(id: string, opts: Map<string, number>): Promise<{ a: T }> {
  return fetch(id);
}
const save = async (a, b) => { await put(a, b); };
class Repo extends Base {
  get(key) { return this.m[key]; }
  handle = (e) => { e.stop(); };
}
items.map(x => { return x * 2; });
type Fn = (x: number) => void;
interface Port { cb: (x: number) => { a: string } }
if (ready) { start(); }
const double = (n: number): number => n * 2;
"""


class JavaScriptFunctionsTest(unittest.TestCase):
    def setUp(self):
        scan = scan_source(SOURCE)
        self.pairs = match_brackets(scan.code)
        self.code = scan.code
        self.functions = {f.name: f for f in find_functions(scan, self.pairs)}

    def test_finds_declarations_methods_and_arrows(self):
        self.assertEqual(set(self.functions), {"load", "save", "get", "handle", "items.map callback", "double"})
        self.assertEqual(self.functions["load"].params, 2)
        self.assertEqual(self.functions["save"].line, 4)
        self.assertFalse(self.functions["double"].block)

    def test_count_params(self):
        self.assertEqual(count_params("a, { b, c }: Opts, d = f(1, 2),"), 3)
        self.assertEqual(count_params("this: Window, e: Event"), 1)
        self.assertEqual(count_params("  "), 0)

    def test_type_spans_cover_aliases_and_interfaces(self):
        spans = type_spans(self.code, self.pairs)
        self.assertEqual(len(spans), 2)


if __name__ == "__main__":
    unittest.main()
