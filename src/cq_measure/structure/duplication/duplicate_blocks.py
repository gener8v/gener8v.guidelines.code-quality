"""Rule 7.1: do not copy blocks of code."""

from __future__ import annotations

import ast
import re
from collections import defaultdict

from cq_measure.codebase import CODE_LANGUAGES, SCRIPT_LANGUAGES, is_testish

_BRACKETS_ONLY = re.compile(r"^[\[\](){};,]*$")
_SCRIPT_IMPORT = re.compile(
    r"\bimport\b[^;]*?\bfrom\s*[\"'][^\"']*[\"'];?|\bimport\s*[\"'][^\"']*[\"'];?"
    r"|\bexport\s*(?:type\s*)?(?:\*|\{[^}]*\})\s*from\s*[\"'][^\"']*[\"'];?"
)


def import_lines(workspace, source) -> set[int]:
    """Return the line numbers that belong to import statements."""
    lines: set[int] = set()
    if source.language == "python":
        tree = workspace.python_tree(source)
        for node in ast.walk(tree) if tree else ():
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                lines.update(range(node.lineno, (node.end_lineno or node.lineno) + 1))
    elif source.language in SCRIPT_LANGUAGES:
        scan = workspace.scan(source)
        for match in _SCRIPT_IMPORT.finditer(scan.code):
            lines.update(range(scan.line_of(match.start()), scan.line_of(match.end() - 1) + 1))
    return lines


def normalized_lines(workspace, source) -> list[tuple[int, str]]:
    """Return (line number, text without whitespace), without blank, import, and bracket-only lines."""
    skipped = import_lines(workspace, source)
    kept = []
    for number, line in enumerate(source.lines, start=1):
        compact = "".join(line.split())
        if compact and number not in skipped and not _BRACKETS_ONLY.match(compact):
            kept.append((number, compact))
    return kept


def _eligible(workspace, source) -> bool:
    return source.language in CODE_LANGUAGES and not is_testish(source.path) and not workspace.generated(source)


def find_duplicates(normalized: dict[str, list], size: int, min_chars: int) -> dict[str, list]:
    """Return, per path, (window index, (first path, first index)) for each repeated window."""
    first_seen: dict[int, tuple[str, int]] = {}
    repeats: dict[str, list] = defaultdict(list)
    for path in sorted(normalized):
        lines = normalized[path]
        for index in range(len(lines) - size + 1):
            text = "\n".join(compact for _number, compact in lines[index : index + size])
            if len(text) < min_chars:
                continue
            first = first_seen.setdefault(hash(text), (path, index))
            if first[0] != path or index - first[1] >= size:
                repeats[path].append((index, first))
    return repeats


def check_duplicate_block(workspace, emit) -> None:
    size = emit.option("min_lines", 8)
    normalized = {s.path: normalized_lines(workspace, s) for s in workspace.sources if _eligible(workspace, s)}
    for path, hits in sorted(find_duplicates(normalized, size, emit.option("min_chars", 160)).items()):
        for start, end, first in _runs(hits):
            other_path, other_index = first
            count = end - start + size
            line = normalized[path][start][0]
            other_line = normalized[other_path][other_index][0]
            emit.flag((path, line), f"{count} lines repeat `{other_path}:{other_line}`. Extract the shared rule into one function.")


def _runs(hits: list) -> list[tuple[int, int, tuple]]:
    runs = []
    for index, first in hits:
        if runs and index == runs[-1][1] + 1:
            runs[-1] = (runs[-1][0], index, runs[-1][2])
        else:
            runs.append((index, index, first))
    return runs
