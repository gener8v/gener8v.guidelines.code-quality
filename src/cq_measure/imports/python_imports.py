"""Extract imports from a Python syntax tree."""

from __future__ import annotations

import ast
from dataclasses import dataclass


@dataclass(frozen=True)
class PythonImport:
    """`import a.b` (names empty) or `from ..a import x, y` (level 2, names x and y)."""

    line: int
    module: str
    level: int
    names: tuple[str, ...]
    type_only: bool


def python_imports(tree: ast.AST) -> list[PythonImport]:
    """Return every import in the tree. Imports under `if TYPE_CHECKING:` are type-only."""
    found: list[PythonImport] = []
    _collect(tree, found, type_only=False)
    return found


def _collect(node: ast.AST, found: list[PythonImport], *, type_only: bool) -> None:
    for child in ast.iter_child_nodes(node):
        if isinstance(child, ast.Import):
            found.extend(PythonImport(child.lineno, alias.name, 0, (), type_only) for alias in child.names)
        elif isinstance(child, ast.ImportFrom):
            names = tuple(alias.name for alias in child.names)
            found.append(PythonImport(child.lineno, child.module or "", child.level, names, type_only))
        else:
            _collect(child, found, type_only=type_only or _is_type_checking(child))


def _is_type_checking(node: ast.AST) -> bool:
    if not isinstance(node, ast.If):
        return False
    test = node.test
    return (isinstance(test, ast.Name) and test.id == "TYPE_CHECKING") or (
        isinstance(test, ast.Attribute) and test.attr == "TYPE_CHECKING"
    )
