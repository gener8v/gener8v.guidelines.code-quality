"""Find the exported names of a TypeScript or JavaScript file."""

from __future__ import annotations

import re
from dataclasses import dataclass

from cq_measure.codebase import Scan

_DECLARED = re.compile(
    r"\bexport\s+(default\s+)?(?:declare\s+)?(?:abstract\s+)?(?:async\s+)?"
    r"(function\*?|class|const|let|var|interface|type|enum)\s+([A-Za-z_$][\w$]*)"
)
_LOCAL_LIST = re.compile(r"\bexport\s+(type\s+)?\{([^}]*)\}(?!\s*from)")
_COMPONENT_VALUE = re.compile(
    r"\s*(?::[^=;]{1,120})?=\s*(?:async\s*)?(?:\(|[A-Za-z_$][\w$]*\s*=>|function\b|(?:React\.)?(?:memo|forwardRef)\b)"
)
_PASCAL = re.compile(r"^[A-Z][A-Za-z0-9]*$")
VALUE_KINDS = frozenset({"function", "function*", "class", "const", "let", "var", "enum", "local"})


@dataclass(frozen=True)
class ScriptExport:
    """One exported name. `component` marks a React component in a TSX or JSX file."""

    name: str
    line: int
    kind: str
    default: bool = False
    component: bool = False

    @property
    def is_value(self) -> bool:
        return self.kind in VALUE_KINDS

    @property
    def is_concept(self) -> bool:
        """Return True for an exported class or React component (rule 1.2)."""
        return self.kind == "class" or self.component


def script_exports(scan: Scan, *, jsx: bool) -> list[ScriptExport]:
    """Return the exports declared in a file. Re-exports (`export ... from`) are not included."""
    found = [_declared(scan, match, jsx=jsx) for match in _DECLARED.finditer(scan.code)]
    for match in _LOCAL_LIST.finditer(scan.code):
        kind = "type" if match.group(1) else "local"
        line = scan.line_of(match.start())
        found.extend(ScriptExport(name, line, kind) for name in _list_names(match.group(2)))
    return found


def _declared(scan: Scan, match: re.Match, *, jsx: bool) -> ScriptExport:
    kind, name = match.group(2), match.group(3)
    component = jsx and bool(_PASCAL.match(name)) and _looks_like_component(scan.code, match, kind)
    return ScriptExport(name, scan.line_of(match.start()), kind, bool(match.group(1)), component)


def _looks_like_component(code: str, match: re.Match, kind: str) -> bool:
    if kind.startswith("function"):
        return True
    if kind in ("const", "let"):
        return bool(_COMPONENT_VALUE.match(code, match.end()))
    return False


def _list_names(body: str) -> list[str]:
    names = []
    for item in body.split(","):
        words = item.split()
        if words and words[0] != "type":
            names.append(words[0])
        elif len(words) > 1:
            names.append(words[1])
    return [name for name in names if re.match(r"^[A-Za-z_$][\w$]*$", name)]
