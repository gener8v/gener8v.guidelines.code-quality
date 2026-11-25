"""Rule 11.3: do not escape the type system."""

from __future__ import annotations

import ast
import re

from cq_measure.source.language import SCRIPT_LANGUAGES, is_declaration

_TS_ANY = re.compile(r":\s*any\b(?![\w$])|\bas\s+any\b(?![\w$])|<any>")
_TS_DIRECTIVE = re.compile(r"@ts-(?:ignore|nocheck)\b")
_ESLINT_DISABLE = re.compile(r"\beslint-disable(?:-next-line|-line)?\b")
_PY_IGNORE = re.compile(r"\btype:\s*ignore\b(?!\[)")


def script_escapes(workspace, source) -> dict[int, set[str]]:
    """Return, per line, the type escapes found in a TypeScript or JavaScript file."""
    found: dict[int, set[str]] = {}
    scan = workspace.scan(source)
    for match in _TS_ANY.finditer(scan.code):
        found.setdefault(scan.line_of(match.start()), set()).add("`any`")
    for comment in scan.comments:
        directive = _TS_DIRECTIVE.search(comment.text)
        if directive:
            found.setdefault(comment.line, set()).add(f"`{directive.group()}`")
        eslint = _ESLINT_DISABLE.search(comment.text)
        if eslint and "--" not in comment.text[eslint.end() :]:
            found.setdefault(comment.line, set()).add("`eslint-disable` without a `--` reason")
    return found


def python_escapes(workspace, source) -> dict[int, set[str]]:
    """Return, per line, the type escapes found in a Python file."""
    found: dict[int, set[str]] = {}
    for comment in workspace.comments(source):
        if _PY_IGNORE.search(comment.text):
            found.setdefault(comment.line, set()).add("`# type: ignore` without an error code")
    tree = workspace.python_tree(source)
    if tree is None:
        return found
    casts = _cast_names(tree)
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and not node.name.startswith("_") and _uses_any(node):
            found.setdefault(node.lineno, set()).add("`Any` in a public signature")
        elif isinstance(node, ast.Call) and _is_cast(node.func, casts):
            found.setdefault(node.lineno, set()).add("`cast()`")
    return found


def _uses_any(node) -> bool:
    arguments = [*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs, node.args.vararg, node.args.kwarg]
    annotations = [arg.annotation for arg in arguments if arg is not None and arg.annotation is not None]
    annotations += [node.returns] if node.returns is not None else []
    return any(_is_any(part) for annotation in annotations for part in ast.walk(annotation))


def _is_any(node) -> bool:
    return (isinstance(node, ast.Name) and node.id == "Any") or (isinstance(node, ast.Attribute) and node.attr == "Any")


def _cast_names(tree) -> set[str]:
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module in ("typing", "typing_extensions"):
            names.update(alias.asname or alias.name for alias in node.names if alias.name == "cast")
    return names


def _is_cast(func, casts: set[str]) -> bool:
    if isinstance(func, ast.Name):
        return func.id in casts
    return isinstance(func, ast.Attribute) and func.attr == "cast" and isinstance(func.value, ast.Name) and func.value.id == "typing"


def check_type_escape(workspace, emit) -> None:
    for source in workspace.sources:
        if workspace.generated(source) or is_declaration(source.path):
            continue
        if source.language == "python":
            found = python_escapes(workspace, source)
        elif source.language in SCRIPT_LANGUAGES:
            found = script_escapes(workspace, source)
        else:
            continue
        for line, kinds in sorted(found.items()):
            emit.flag((source.path, line), f"Type escape: {', '.join(sorted(kinds))}. Give the value a real type, or explain the exception.")
