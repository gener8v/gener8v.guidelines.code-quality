import unittest

from cq_measure.codebase import scan_source
from cq_measure.structure.classes.script_classes import script_classes
from cq_measure.structure.functions import find_functions, match_brackets

SOURCE = """export abstract class Store<T> extends Base implements IStore<T>, Clock {
  abstract load(id: string): T;
  save(x) { const f = () => { return 1; }; return f; }
  get size() { return 1; }
}
export interface IStore<T> extends Reader, Writer {
  get(id: string): T;
  put?(id: string, value: T): void;
  nested: { inner(): void };
  label: string;
}
"""


class ScriptClassesTest(unittest.TestCase):
    def test_classes_and_interfaces(self):
        scan = scan_source(SOURCE)
        pairs = match_brackets(scan.code)
        found = {c.name: c for c in script_classes(scan, find_functions(scan, pairs), pairs)}
        store = found["Store"]
        self.assertEqual((store.kind, store.bases, store.implements), ("abstract", ("Base",), ("IStore", "Clock")))
        self.assertEqual(sorted(store.methods), ["load", "save", "size"])
        port = found["IStore"]
        self.assertEqual((port.kind, port.bases, port.methods), ("interface", ("Reader", "Writer"), ("get", "put")))


if __name__ == "__main__":
    unittest.main()
