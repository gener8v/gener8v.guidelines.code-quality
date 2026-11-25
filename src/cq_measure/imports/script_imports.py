"""Extract import specifiers from lexed TypeScript and JavaScript."""

from __future__ import annotations

import re
from dataclasses import dataclass

from cq_measure.source.scan import Scan

_BEFORE_SPECIFIER = re.compile(r"(?:\bfrom|\bimport|\brequire\s*\(|\bimport\s*\()\s*\Z")
_STATEMENT_KEYWORD = re.compile(r"\b(import|export)\b(\s+type\b)?")


@dataclass(frozen=True)
class ScriptImport:
    """An import specifier such as `./billing` and the line that holds it."""

    line: int
    specifier: str
    type_only: bool


def script_imports(scan: Scan) -> list[ScriptImport]:
    """Return the specifiers of import, export-from, require, and dynamic import."""
    found = []
    for start, _end, value in scan.strings:
        before = scan.code[max(0, start - 300) : start]
        if not value or not _BEFORE_SPECIFIER.search(before):
            continue
        found.append(ScriptImport(scan.line_of(start), value, _is_type_only(before)))
    return found


def _is_type_only(before: str) -> bool:
    keywords = list(_STATEMENT_KEYWORD.finditer(before))
    return bool(keywords) and keywords[-1].group(2) is not None


def climb_of(specifier: str) -> int:
    """Return how many `../` steps a relative specifier takes."""
    return sum(1 for part in specifier.split("/") if part == "..")
