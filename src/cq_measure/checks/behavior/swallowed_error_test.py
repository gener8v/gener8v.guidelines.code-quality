import unittest

from cq_measure.fixture_repository import findings_for

PY = """try:
    run()
except ValueError:
    pass
try:
    run()
except:
    log()
try:
    run()
except:
    cleanup()
    raise
try:
    run()
except OSError as error:
    log(error)
"""

TS = """try { run(); } catch (e) { /* ignore */ }
try { run(); } catch { }
load().catch(() => {});
load().catch(() => null);
load().catch((e) => report(e));
try { run(); } catch (e) { report(e); }
"""


class SwallowedErrorTest(unittest.TestCase):
    def test_python(self):
        found = findings_for({"a.py": PY}, "swallowed-error")
        self.assertEqual([(f.line, f.severity) for f in found], [(3, "fail"), (7, "fail")])

    def test_typescript(self):
        self.assertEqual([f.line for f in findings_for({"a.ts": TS}, "swallowed-error")], [1, 2, 3, 4])


if __name__ == "__main__":
    unittest.main()
