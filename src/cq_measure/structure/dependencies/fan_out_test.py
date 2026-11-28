import unittest

from cq_measure.testing import findings_for


def _repo(count, importer="src/hub.ts"):
    files = {f"src/m{i}.ts": "" for i in range(count)}
    files[importer] = "".join(f"import x{i} from './m{i}';\n" for i in range(count))
    return files


class FanOutTest(unittest.TestCase):
    def test_too_many_imports(self):
        self.assertEqual([f.severity for f in findings_for(_repo(13), "fan-out")], ["warn"])
        self.assertEqual([f.severity for f in findings_for(_repo(21), "fan-out")], ["fail"])

    def test_barrels_and_small_files(self):
        self.assertEqual(findings_for(_repo(21, "src/index.ts"), "fan-out"), [])
        self.assertEqual(findings_for(_repo(12), "fan-out"), [])


if __name__ == "__main__":
    unittest.main()
