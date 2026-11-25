"""Rule 12.1: do not swallow errors."""

from __future__ import annotations

import ast
import re

from cq_measure.source.language import SCRIPT_LANGUAGES

_EMPTY_CATCH = re.compile(r"\bcatch\s*(?:\([^()]*\))?\s*\{\s*\}")
_NOOP_PROMISE_CATCH = re.compile(
    r"\.catch\(\s*(?:async\s*)?(?:\(\s*[\w$]*\s*(?::\s*[\w$]+)?\s*\)|[\w$]+)\s*=>\s*(?:\{\s*\}|null|undefined|void\s+0)\s*\)"
    r"|\.catch\(\s*function\s*\([^()]*\)\s*\{\s*\}\s*\)"
)
NOOP_STATEMENTS = (ast.Pass, ast.Continue)


def python_swallows(tree: ast.AST) -> list[tuple[int, str]]:
    """Return (line, message) for empty handlers and bare `except:` clauses that do not re-raise."""
    found = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.ExceptHandler):
            continue
        if all(_is_noop(statement) for statement in node.body):
            found.append((node.lineno, "The `except` block does nothing, so the error disappears."))
        elif node.type is None and not _reraises(node):
            found.append((node.lineno, "A bare `except:` catches every error, including interrupts."))
    return found


def _is_noop(statement) -> bool:
    if isinstance(statement, NOOP_STATEMENTS):
        return True
    return isinstance(statement, ast.Expr) and isinstance(statement.value, ast.Constant) and statement.value.value is Ellipsis


def _reraises(handler: ast.ExceptHandler) -> bool:
    return any(isinstance(node, ast.Raise) and node.exc is None for node in ast.walk(handler))


def script_swallows(scan) -> list[tuple[int, str]]:
    found = [(scan.line_of(m.start()), "The `catch` block is empty, so the error disappears.") for m in _EMPTY_CATCH.finditer(scan.code)]
    found += [(scan.line_of(m.start()), "The `.catch()` handler does nothing, so the error disappears.") for m in _NOOP_PROMISE_CATCH.finditer(scan.code)]
    return found


def check_swallowed_error(workspace, emit) -> None:
    advice = "Handle it, log it with context, or let it propagate."
    for source in workspace.sources:
        if workspace.generated(source):
            continue
        if source.language == "python":
            tree = workspace.python_tree(source)
            found = python_swallows(tree) if tree else []
        elif source.language in SCRIPT_LANGUAGES:
            found = script_swallows(workspace.scan(source))
        else:
            continue
        for line, message in found:
            emit.flag((source.path, line), f"{message} {advice}")
