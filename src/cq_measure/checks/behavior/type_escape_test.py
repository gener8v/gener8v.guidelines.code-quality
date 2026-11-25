import unittest

from cq_measure.fixture_repository import findings_for

TS = """const a: any = 1;
const b = load() as any;
// @ts-ignore
call(b);
// eslint-disable-next-line no-console
// eslint-disable-next-line no-console -- startup banner
const ok: string = 'any';
"""

PY = """from typing import Any, cast


def public(value: Any) -> int:
    return cast(int, value)


def _private(value: Any):
    return value  # type: ignore


x = 1  # type: ignore[assignment]
"""


class TypeEscapeTest(unittest.TestCase):
    def test_typescript(self):
        found = findings_for({"a.ts": TS}, "type-escape")
        self.assertEqual([f.line for f in found], [1, 2, 3, 5])

    def test_python(self):
        found = findings_for({"a.py": PY}, "type-escape")
        self.assertEqual([f.line for f in found], [4, 5, 9])

    def test_clean(self):
        self.assertEqual(findings_for({"a.ts": "const a: unknown = 1;\nconst many = 2;\n"}, "type-escape"), [])


if __name__ == "__main__":
    unittest.main()
