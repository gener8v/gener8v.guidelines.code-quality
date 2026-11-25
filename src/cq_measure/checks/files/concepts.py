"""Rules 1.2 and 1.3: one concept per file, and a file name that matches it."""

from __future__ import annotations

import ast
import re

from cq_measure.source.language import SCRIPT_LANGUAGES
from cq_measure.source.roles import is_framework_file, is_testish

ENTRY_STEMS = frozenset({"index", "__init__", "__main__", "main", "app", "mod", "lib"})
_EXCEPTION_NAME = re.compile(r"(Error|Exception|Warning)$")
_SEPARATORS = re.compile(r"[-_.\s]")
_WORDS = re.compile(r"[A-Z]+(?![a-z])|[A-Z]?[a-z0-9]+")


def concepts_of(workspace, source) -> tuple[list[tuple[str, int, str]], int]:
    """Return the public classes or components of a file (name, line, kind) and its count of public values."""
    if source.language == "python":
        return _python_concepts(workspace, source)
    if source.language in SCRIPT_LANGUAGES:
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


def _measured(workspace, source) -> bool:
    if is_testish(source.path) or workspace.generated(source) or is_framework_file(source.path):
        return False
    return ".stories." not in source.name


def check_one_concept(workspace, emit) -> None:
    for source in workspace.sources:
        if not _measured(workspace, source) or source.stem in ENTRY_STEMS:
            continue
        concepts, _values = concepts_of(workspace, source)
        if len(concepts) > 1:
            names = ", ".join(f"`{name}`" for name, _line, _kind in concepts)
            message = f"{len(concepts)} public classes or components ({names}). Move each into its own file."
            emit.flag((source.path, concepts[1][1]), message)


def check_name_matches_export(workspace, emit) -> None:
    for source in workspace.sources:
        if not _measured(workspace, source):
            continue
        concepts, values = concepts_of(workspace, source)
        if len(concepts) != 1 or values != 1:
            continue
        name, line, kind = concepts[0]
        stem = source.directory.rsplit("/", 1)[-1] if source.stem in ENTRY_STEMS else source.stem
        if stem and normalize(stem) != normalize(name):
            suggestion = suggest_name(name, source)
            emit.flag((source.path, line), f"The file holds one {kind}, `{name}`, but is named `{source.name}`. Rename it to `{suggestion}`.")


def normalize(name: str) -> str:
    """Lowercase a name and drop separators, so `invoice_service` equals `InvoiceService`."""
    return _SEPARATORS.sub("", name).lower()


def suggest_name(name: str, source) -> str:
    words = [word.lower() for word in _WORDS.findall(name)]
    extension = source.name[len(source.stem) :]
    if source.language == "python":
        return "_".join(words) + extension
    if source.language in ("tsx", "jsx") and source.stem[:1].isupper():
        return name + extension
    return "-".join(words) + extension
