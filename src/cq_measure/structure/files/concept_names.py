"""The concept names of a file: its exports, classes, and normalized stem."""

from __future__ import annotations

import ast
import re

from cq_measure.codebase import JAVASCRIPT_LANGUAGES, is_framework_file, is_testish

ENTRY_STEMS = frozenset({"index", "__init__", "__main__", "main", "app", "mod", "lib"})


_EXCEPTION_NAME = re.compile(r"(Error|Exception|Warning)$")


def concepts_of(workspace, source) -> tuple[list[tuple[str, int, str]], int]:
    """Return the public classes or components of a file (name, line, kind) and its count of public values."""
    if source.language == "python":
        return _python_concepts(workspace, source)
    if source.language in JAVASCRIPT_LANGUAGES:
        exports = workspace.exports(source)
        concepts = [(e.name, e.line, "component" if e.component else "class") for e in exports if e.is_concept]
        return concepts, len({e.name for e in exports if e.is_value})
    return [], 0


def _python_concepts(workspace, source) -> tuple[list[tuple[str, int, str]], int]:
    tree = workspace.python_tree(source)
    if tree is None:
        return [], 0
    definitions = (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
    public = [node for node in tree.body if isinstance(node, definitions) and not node.name.startswith("_")]
    classes = [(n.name, n.lineno, "class") for n in public if isinstance(n, ast.ClassDef)]
    concepts = [item for item in classes if not _EXCEPTION_NAME.search(item[0])]
    return concepts, len(public)


def holds_concepts(workspace, source) -> bool:
    if is_testish(source.path) or workspace.generated(source) or is_framework_file(source.path):
        return False
    return ".stories." not in source.name


_SEPARATORS = re.compile(r"[-_.\s]")


def normalize(name: str) -> str:
    """Lowercase a name and drop separators, so `invoice_service` equals `InvoiceService`."""
    return _SEPARATORS.sub("", name).lower()
