"""Rule 7.3: delete unused functions, classes, and exports."""

from __future__ import annotations

import ast
import re

from cq_measure.codebase import (
    SCRIPT_LANGUAGES,
    in_route_tree,
    is_config_name,
    is_declaration,
    is_framework_file,
    is_testish,
)

FRAMEWORK_EXPORTS = frozenset(
    "GET POST PUT PATCH DELETE HEAD OPTIONS metadata generateMetadata generateStaticParams viewport dynamic "
    "dynamicParams revalidate runtime preferredRegion maxDuration fetchCache config loader action meta links "
    "headers handle ErrorBoundary getStaticPaths getStaticProps getServerSideProps prerender main handler".split()
)
EXEMPT_STEMS = frozenset({"__init__", "__main__", "index", "conftest", "setup", "manage"})


def python_public_names(tree: ast.Module) -> list[tuple[str, int]]:
    """Return the public top-level functions and classes that no framework decorator registers."""
    found = []
    for node in tree.body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) or node.name.startswith("_"):
            continue
        if any(_registers(decorator) for decorator in node.decorator_list):
            continue
        found.append((node.name, node.lineno))
    return found


def _registers(decorator: ast.expr) -> bool:
    target = decorator.func if isinstance(decorator, ast.Call) else decorator
    return isinstance(target, ast.Attribute)


def _declared_names(workspace, source) -> list[tuple[str, int]]:
    if source.language == "python":
        tree = workspace.python_tree(source)
        return python_public_names(tree) if tree else []
    if source.language in SCRIPT_LANGUAGES:
        return [(e.name, e.line) for e in workspace.exports(source) if not e.default]
    return []


def _skipped(workspace, source) -> bool:
    if is_testish(source.path) or is_declaration(source.path) or source.stem in EXEMPT_STEMS:
        return True
    if is_config_name(source.name) or is_framework_file(source.path) or ".stories." in source.name:
        return True
    return workspace.generated(source)


def used_in_own_file(name: str, text: str) -> bool:
    """Return True when the name occurs more than once (its definition plus a use) in the file."""
    return len(re.findall(rf"(?<![\w$]){re.escape(name)}(?![\w$])", text)) > 1


def check_unused_symbol(workspace, emit) -> None:
    public = set(workspace.config["public_symbols"]) | FRAMEWORK_EXPORTS
    for source in workspace.sources:
        if _skipped(workspace, source):
            continue
        for name, line in _declared_names(workspace, source):
            if name in public or workspace.mentions[name] > 1 or used_in_own_file(name, source.text):
                continue
            if in_route_tree(source.path) and name[:1].isupper():
                continue
            emit.flag((source.path, line), f"`{name}` is not used anywhere. Delete it, or list it in `public_symbols` if other repositories use it.")
