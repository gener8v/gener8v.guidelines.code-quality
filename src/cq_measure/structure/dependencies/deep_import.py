"""Rule 3.2: do not import the internals of another package."""

from __future__ import annotations

import posixpath
import re

from cq_measure.codebase import SCRIPT_LANGUAGES, is_testish, is_within, parts_of

_RE_EXPORT = re.compile(r"\bexport\s*(?:type\s*)?(?:\*|\{[^}]*\})\s*(?:as\s+[\w$]+\s*)?from\b")


INDEX_NAMES = tuple(f"index{ext}" for ext in (".ts", ".tsx", ".js", ".jsx", ".mjs", ".mts"))


def barrels(workspace) -> dict[str, str]:
    """Return directories whose `index` file re-exports names, mapped to that index file."""
    found = {}
    for source in workspace.sources:
        if source.name in INDEX_NAMES and source.language in SCRIPT_LANGUAGES:
            if _RE_EXPORT.search(workspace.scan(source).code):
                found.setdefault(source.directory, source.path)
    return found


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
        return None
    directory = bypassed_barrel(path, record.target, entries)
    if directory:
        return f"`{record.specifier}` reaches past the entry point of `{directory}/`. Import from `{entries[directory]}` instead."
    return None
