"""Measure Python functions exactly from the syntax tree."""

from __future__ import annotations

import ast

from cq_measure.structure.functions.function_measure import FunctionMeasure

FUNCTIONS = (ast.FunctionDef, ast.AsyncFunctionDef)
SCOPES = (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef)
BLOCKS = (ast.If, ast.For, ast.AsyncFor, ast.While, ast.Try, ast.With, ast.AsyncWith, ast.Match) + (
    (ast.TryStar,) if hasattr(ast, "TryStar") else ()
)
BRANCHES = (ast.If, ast.For, ast.AsyncFor, ast.While, ast.IfExp, ast.ExceptHandler, ast.match_case)
RECEIVERS = frozenset({"self", "cls", "mcs", "metacls"})


def measure_python(tree: ast.AST, lines: list[str]) -> list[FunctionMeasure]:
    """Return a measure for every function and method in the tree, nested ones included."""
    return [_measure(node, lines) for node in ast.walk(tree) if isinstance(node, FUNCTIONS)]


def _measure(node, lines: list[str]) -> FunctionMeasure:
    return FunctionMeasure(
        name=node.name,
        line=node.lineno,
        lines=body_lines(node, lines),
        nesting=nesting(node),
        complexity=complexity(node),
        params=len(parameters(node)),
        flag_params=flag_params(node),
    )


def body_lines(node, lines: list[str]) -> int:
    """Count the non-blank lines of the body, without the docstring."""
    body = node.body[1:] if _has_docstring(node) else node.body
    if not body:
        return 0
    return sum(1 for line in lines[body[0].lineno - 1 : node.end_lineno] if line.strip())


def _has_docstring(node) -> bool:
    first = node.body[0] if node.body else None
    return isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant) and isinstance(first.value.value, str)


def own_nodes(node):
    """Yield the nodes inside a function, but not inside nested functions, lambdas, or classes."""
    stack = list(ast.iter_child_nodes(node))
    while stack:
        child = stack.pop()
        yield child
        if not isinstance(child, SCOPES):
            stack.extend(ast.iter_child_nodes(child))


def complexity(node) -> int:
    """Cyclomatic complexity: one, plus one per branch, loop, handler, case, and boolean operator."""
    total = 1
    for child in own_nodes(node):
        if isinstance(child, BRANCHES):
            total += 1
        elif isinstance(child, ast.BoolOp):
            total += len(child.values) - 1
        elif isinstance(child, ast.comprehension):
            total += 1 + len(child.ifs)
    return total


def nesting(node, depth: int = 0) -> int:
    """Return the deepest level of nested blocks. An `elif` stays at the level of its `if`."""
    deepest = depth
    for child in ast.iter_child_nodes(node):
        if isinstance(child, SCOPES):
            continue
        if isinstance(child, BLOCKS):
            elif_branch = isinstance(node, ast.If) and isinstance(child, ast.If) and node.orelse == [child]
            deepest = max(deepest, nesting(child, depth if elif_branch else depth + 1))
        else:
            deepest = max(deepest, nesting(child, depth))
    return deepest


def parameters(node) -> list[ast.arg]:
    """Return the parameters without `self`/`cls`, `*args`, and `**kwargs`."""
    params = [*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs]
    if params and params[0].arg in RECEIVERS:
        params = params[1:]
    return params


def flag_params(node) -> tuple[str, ...]:
    """Return positional parameters typed `bool` or defaulting to True or False."""
    if node.name.startswith("__") or node.name.startswith("test") or _is_registered(node):
        return ()
    positional = [*node.args.posonlyargs, *node.args.args]
    defaults = [None] * (len(positional) - len(node.args.defaults)) + list(node.args.defaults)
    return tuple(arg.arg for arg, default in zip(positional, defaults) if _is_bool(arg.annotation, default))


def _is_registered(node) -> bool:
    """Return True for a property setter or a function that a framework registers, such as `@app.get(...)`."""
    targets = (d.func if isinstance(d, ast.Call) else d for d in node.decorator_list)
    return any(isinstance(target, ast.Attribute) for target in targets)


def _is_bool(annotation, default) -> bool:
    if isinstance(annotation, ast.Name) and annotation.id == "bool":
        return True
    if isinstance(annotation, ast.Constant) and annotation.value == "bool":
        return True
    return isinstance(default, ast.Constant) and isinstance(default.value, bool)


def has_logic(tree: ast.AST) -> bool:
    """Return True when a function or method has a body beyond `pass`, `...`, or `raise NotImplementedError`."""
    return any(isinstance(node, FUNCTIONS) and not _is_stub(node) for node in ast.walk(tree))


def _is_stub(node) -> bool:
    body = node.body[1:] if _has_docstring(node) else node.body
    return all(_is_stub_statement(statement) for statement in body)


def _is_stub_statement(statement) -> bool:
    if isinstance(statement, ast.Pass):
        return True
    if isinstance(statement, ast.Expr) and isinstance(statement.value, ast.Constant):
        return True
    return isinstance(statement, ast.Raise) and "NotImplementedError" in ast.dump(statement)
