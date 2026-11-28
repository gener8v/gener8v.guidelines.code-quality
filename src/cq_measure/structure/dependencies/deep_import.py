"""Rule 3.2: do not import the internals of another package."""

from __future__ import annotations

import ast
import posixpath
import re

from cq_measure.codebase import SCRIPT_LANGUAGES, is_testish, is_within, parts_of

_RE_EXPORT = re.compile(r"\bexport\s*(?:type\s*)?(?:\*|\{[^}]*\})\s*(?:as\s+[\w$]+\s*)?from\b")


INDEX_NAMES = tuple(f"index{ext}" for ext in (".ts", ".tsx", ".js", ".jsx", ".mjs", ".mts"))


def barrels(workspace) -> dict[str, str]:
    """Return the directories that declare an entry point, mapped to the entry file.

    TypeScript and JavaScript: an `index` file that re-exports names. Python: an
    `__init__.py` that sets `__all__` or re-exports names with a relative import.
    """
    found = {}
    for source in workspace.sources:
        if source.name in INDEX_NAMES and source.language in SCRIPT_LANGUAGES:
            if _RE_EXPORT.search(workspace.scan(source).code):
                found.setdefault(source.directory, source.path)
        elif source.name == "__init__.py" and declares_api(workspace.python_tree(source)):
            found.setdefault(source.directory, source.path)
    return found


def declares_api(tree: ast.Module | None) -> bool:
    """Return True when a Python `__init__.py` sets `__all__` or re-exports names from its own modules."""
    if tree is None:
        return False
    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and node.level > 0:
            return True
        targets = node.targets if isinstance(node, ast.Assign) else [node.target] if isinstance(node, ast.AnnAssign) else []
        if any(isinstance(target, ast.Name) and target.id == "__all__" for target in targets):
            return True
    return False


def bypassed_barrel(importer: str, target: str, entries: dict[str, str]) -> str | None:
    """Return the outermost directory whose entry point the import goes around, or None."""
    parts = parts_of(posixpath.dirname(target))
    for depth in range(1, len(parts) + 1):
        directory = "/".join(parts[:depth])
        if is_within(importer, directory):
            continue
        if directory in entries and entries[directory] != target:
            return directory
    return None


def names_the_package(record, directory: str) -> bool:
    """Return True for `from billing import total` when `billing/total.py` also exists.

    The import names the package, so it goes through `__init__.py`. Python
    resolves the name to the module file only because the two names are equal.
    """
    named = record.specifier.lstrip(".").rsplit(".", 1)[-1]
    return posixpath.dirname(record.target) == directory and named == posixpath.basename(directory)


def _private_part(target: str, names: tuple[str, ...]) -> tuple[str, str] | None:
    """Return (private name, its package directory) for an import of a `_private` module or name."""
    parts = target.split("/")
    for index, part in enumerate(parts):
        stem = posixpath.splitext(part)[0]
        if stem.startswith("_") and not stem.startswith("__"):
            return stem, "/".join(parts[:index])
    for name in names:
        if name.startswith("_") and not name.startswith("__"):
            return name, posixpath.dirname(target)
    return None


def check_deep_import(workspace, emit) -> None:
    entries = barrels(workspace)
    for path, records in sorted(workspace.graph.records.items()):
        if is_testish(path):
            continue
        for record in records:
            if record.target is None:
                continue
            message = _deep_message(path, record, entries)
            if message:
                emit.flag((path, record.line), message)


def _deep_message(path: str, record, entries: dict[str, str]) -> str | None:
    if path.endswith(".py"):
        private = _private_part(record.target, record.names)
        if private and not is_within(path, private[1]):
            return f"Imports the private `{private[0]}` from outside `{private[1] or '.'}/`. Use a public name from the package entry point."
    directory = bypassed_barrel(path, record.target, entries)
    if directory and path.endswith(".py") and names_the_package(record, directory):
        return None
    if directory:
        return f"`{record.specifier}` reaches past the entry point of `{directory}/`. Import from `{entries[directory]}` instead."
    return None
