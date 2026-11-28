"""Describe Python classes: kind, bases, methods, and pass-through shape."""

from __future__ import annotations

import ast

from cq_measure.structure.classes.class_info import ClassInfo
from cq_measure.structure.functions import FUNCTIONS, parameters

ABSTRACT_MARKERS = frozenset({"ABC", "ABCMeta"})


def python_classes(tree: ast.Module) -> list[ClassInfo]:
    """Return every class in the module. `top_level` marks the classes at module level."""
    top = {id(node) for node in tree.body if isinstance(node, ast.ClassDef)}
    return [_describe(node, top_level=id(node) in top) for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]


def _describe(node: ast.ClassDef, *, top_level: bool) -> ClassInfo:
    methods = [item for item in node.body if isinstance(item, FUNCTIONS)]
    return ClassInfo(
        name=node.name,
        line=node.lineno,
        kind=_kind(node, methods),
        bases=tuple(name for name in (base_name(base) for base in node.bases) if name),
        methods=tuple(method.name for method in methods),
        top_level=top_level,
        pass_through_field=pass_through_field(methods),
    )


def base_name(node: ast.expr) -> str | None:
    """Return the simple name of a base class expression: `models.Model` gives `Model`."""
    if isinstance(node, ast.Subscript):
        node = node.value
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return None


def _kind(node: ast.ClassDef, methods) -> str:
    bases = {base_name(base) for base in node.bases}
    if "Protocol" in bases:
        return "protocol"
    metaclass = {base_name(keyword.value) for keyword in node.keywords if keyword.arg == "metaclass"}
    if bases & ABSTRACT_MARKERS or metaclass & ABSTRACT_MARKERS:
        return "abstract"
    if any(_is_abstract(method) for method in methods):
        return "abstract"
    return "class"


def _is_abstract(method) -> bool:
    return any(base_name(decorator) == "abstractmethod" for decorator in method.decorator_list)


def pass_through_field(methods) -> str | None:
    """Return the field when every method except `__init__` only forwards its arguments to it."""
    forwarding = [method for method in methods if method.name != "__init__"]
    fields = {_forwarded_field(method) for method in forwarding}
    if not forwarding or None in fields or len(fields) != 1:
        return None
    return fields.pop()


def _forwarded_field(method) -> str | None:
    call = _single_call(method)
    if call is None or not _same_arguments(call, method):
        return None
    target = call.func
    if not (isinstance(target, ast.Attribute) and isinstance(target.value, ast.Attribute)):
        return None
    owner = target.value
    return owner.attr if isinstance(owner.value, ast.Name) and owner.value.id == "self" else None


def _single_call(method) -> ast.Call | None:
    """Return the call when the body (without a docstring) is one `return call(...)` or `call(...)`."""
    body = [s for s in method.body if not (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant))]
    if len(body) != 1 or not isinstance(body[0], (ast.Return, ast.Expr)):
        return None
    value = body[0].value
    if isinstance(value, ast.Await):
        value = value.value
    return value if isinstance(value, ast.Call) else None


def _same_arguments(call: ast.Call, method) -> bool:
    names = [param.arg for param in parameters(method)]
    positional = [arg.id if isinstance(arg, ast.Name) else None for arg in call.args]
    keywords = [(kw.arg, kw.value.id if isinstance(kw.value, ast.Name) else None) for kw in call.keywords]
    if any(name != value for name, value in keywords):
        return False
    return positional + [name for name, _value in keywords] == names
