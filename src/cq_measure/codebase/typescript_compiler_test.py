import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from cq_measure.codebase.typescript_compiler import measure_with_compiler, parse_reply

REPLY = {
    "version": "5.9.3",
    "files": {
        "a.ts": {
            "functions": [{"name": "load", "line": 1, "lines": 3, "nesting": 1, "complexity": 2, "params": 1}],
            "classes": [{"name": "Port", "line": 5, "kind": "interface", "bases": [], "implements": [], "methods": ["send"]}],
        }
    },
}


def available_compiler() -> str | None:
    """Return the path of a typescript package from CQ_TYPESCRIPT, or None."""
    override = os.environ.get("CQ_TYPESCRIPT", "")
    return override if override and override != "off" and shutil.which("node") else None


class ParseReplyTest(unittest.TestCase):
    def test_reads_functions_and_classes(self):
        result = parse_reply(json.dumps(REPLY), "")
        self.assertEqual(result.version, "5.9.3")
        self.assertEqual(result.functions["a.ts"], REPLY["files"]["a.ts"]["functions"])
        self.assertEqual(result.classes["a.ts"], REPLY["files"]["a.ts"]["classes"])
        self.assertEqual(result.status, {"measured_by": "compiler", "version": "5.9.3"})

    def test_keeps_the_reason_of_an_error(self):
        result = parse_reply(json.dumps({"error": "the typescript package is not installed in the repository"}), "")
        self.assertIsNone(result.version)
        self.assertEqual(result.status["measured_by"], "approximation")
        self.assertIn("not installed", result.status["reason"])

    def test_reports_a_crash_from_stderr(self):
        result = parse_reply("", "trace\nRangeError: Maximum call stack size exceeded\n")
        self.assertEqual(result.reason, "the compiler stopped: RangeError: Maximum call stack size exceeded")


class FallbackTest(unittest.TestCase):
    def test_off_skips_the_compiler(self):
        with mock.patch.dict(os.environ, {"CQ_TYPESCRIPT": "off"}):
            self.assertEqual(measure_with_compiler(Path("."), ["a.ts"]).reason, "CQ_TYPESCRIPT is off")

    def test_no_node(self):
        with mock.patch.dict(os.environ, {"CQ_TYPESCRIPT": ""}), mock.patch("shutil.which", return_value=None):
            self.assertEqual(measure_with_compiler(Path("."), ["a.ts"]).reason, "Node.js is not installed")


@unittest.skipUnless(available_compiler(), "set CQ_TYPESCRIPT to a typescript package to run the compiler")
class CompilerTest(unittest.TestCase):
    def test_measures_a_file(self):
        with tempfile.TemporaryDirectory() as root:
            Path(root, "a.ts").write_text("export function load(id: string) {\n  return id ?? 'x';\n}\n", encoding="utf-8")
            result = measure_with_compiler(Path(root), ["a.ts"])
        self.assertTrue(result.version, result.reason)
        self.assertEqual(result.functions["a.ts"], [{"name": "load", "line": 1, "lines": 1, "nesting": 0, "complexity": 2, "params": 1}])


if __name__ == "__main__":
    unittest.main()
