"""Rules 3.2, 3.3, and 3.4: package entry points, short relative climbs, inward dependencies."""

from __future__ import annotations

import posixpath
import re

from cq_measure.source.language import SCRIPT_LANGUAGES
from cq_measure.source.packages import is_within, parts_of
from cq_measure.source.roles import is_testish

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


def check_relative_climb(workspace, emit) -> None:
    for path, records in sorted(workspace.graph.records.items()):
        for record in records:
            if record.climb:
                text = (f"`{record.specifier}` climbs {record.climb} levels", "Import through the package entry point or a path alias.")
                emit.measure((path, record.line), record.climb, text)


def layer_violation(importer: str, target: str, layers: dict) -> tuple[str, str] | None:
    """Return (inner name, outer name) when inner code imports outer code, below their common directory."""
    importer_parts, target_parts = _below_common(parts_of(posixpath.dirname(importer)), parts_of(posixpath.dirname(target)))
    inner = [part for part in importer_parts if part in layers["inner"]]
    outer = [part for part in target_parts if part in layers["outer"]]
    if inner and outer and not any(part in layers["outer"] for part in importer_parts):
        return inner[0], outer[0]
    return None


def _below_common(first: list[str], second: list[str]) -> tuple[list[str], list[str]]:
    shared = 0
    while shared < min(len(first), len(second)) and first[shared] == second[shared]:
        shared += 1
    return first[shared:], second[shared:]


def check_layer_direction(workspace, emit) -> None:
    layers = workspace.config["layers"]
    for path, targets in sorted(workspace.graph.edges.items()):
        if is_testish(path):
            continue
        for target, record in sorted(targets.items()):
            violation = layer_violation(path, target, layers)
            if violation:
                inner, outer = violation
                emit.flag((path, record.line), f"`{inner}` code imports `{target}` from the outer layer `{outer}`. Define an interface in `{inner}` and implement it outside.")
