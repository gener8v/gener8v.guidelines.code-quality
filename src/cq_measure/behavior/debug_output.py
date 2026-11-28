"""Rule 18.4: no debug output left in source."""

from __future__ import annotations

import ast
import re

from cq_measure.codebase import (
    JAVASCRIPT_LANGUAGES,
    is_cli_entry,
    is_config_name,
    is_declaration,
    is_testish,
)

_CONSOLE = re.compile(r"\bconsole\.(log|debug)\s*\(|(?<![\w$.])debugger(?![\w$])")
DEBUGGER_MODULES = frozenset({"pdb", "ipdb", "pudb"})


def javascript_debug(scan) -> list[tuple[int, str]]:
    found = []
    for match in _CONSOLE.finditer(scan.code):
        label = f"console.{match.group(1)}()" if match.group(1) else "debugger"
        found.append((scan.line_of(match.start()), label))
    return found


def python_debug(tree: ast.AST) -> list[tuple[int, str]]:
    found = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if isinstance(func, ast.Name) and func.id in ("print", "breakpoint"):
            found.append((node.lineno, f"{func.id}()"))
        elif isinstance(func, ast.Attribute) and func.attr == "set_trace" and _module_name(func.value) in DEBUGGER_MODULES:
            found.append((node.lineno, f"{_module_name(func.value)}.set_trace()"))
    return found


def _module_name(node) -> str | None:
    return node.id if isinstance(node, ast.Name) else None


def _findings(workspace, source) -> list[tuple[int, str]]:
    if source.language == "python":
        tree = workspace.python_tree(source)
        return python_debug(tree) if tree else []
    if source.language in JAVASCRIPT_LANGUAGES and not is_declaration(source.path):
        return javascript_debug(workspace.scan(source))
    return []


def check_debug_output(workspace, emit) -> None:
    for source in workspace.sources:
        if is_testish(source.path) or is_config_name(source.name) or workspace.generated(source) or is_cli_entry(source):
            continue
        for line, label in _findings(workspace, source):
            emit.flag((source.path, line), f"Debug output `{label}`. Remove it, or use the project's logger.")
