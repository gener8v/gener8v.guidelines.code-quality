import io
import json
import unittest
from contextlib import redirect_stderr, redirect_stdout

from cq_measure.cli import list_checks, main
from cq_measure.config import load_defaults
from cq_measure.fixture_repository import fixture_repo

LONG = "x = 1\n" * 501


def _run(args):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = main(args)
    return code, out.getvalue(), err.getvalue()


class CliTest(unittest.TestCase):
    def test_exit_codes_follow_fail_on(self):
        with fixture_repo({"src/a.py": LONG}) as root:
            self.assertEqual(_run([str(root), "--only", "file-lines"])[0], 1)
            self.assertEqual(_run([str(root), "--only", "file-lines", "--fail-on", "never"])[0], 0)

    def test_json_and_paths(self):
        with fixture_repo({"src/a.py": LONG, "lib/b.py": LONG}) as root:
            code, out, _err = _run([str(root), "--only", "file-lines", "--format", "json", "--paths", "lib"])
        self.assertEqual([f["path"] for f in json.loads(out)["findings"]], ["lib/b.py"])
        self.assertEqual(code, 1)

    def test_usage_errors_exit_2(self):
        with fixture_repo({".code-quality.json": "{"}) as root:
            code, _out, err = _run([str(root)])
        self.assertEqual(code, 2)
        self.assertIn("not valid JSON", err)
        self.assertEqual(_run(["/no/such/dir"])[0], 2)
        with fixture_repo({"a.py": ""}) as root:
            self.assertEqual(_run([str(root), "--only", "nope"])[0], 2)

    def test_list_checks(self):
        listing = list_checks(load_defaults())
        self.assertIn("file-lines", listing)
        self.assertIn("tests: warn > 500", listing)


if __name__ == "__main__":
    unittest.main()
