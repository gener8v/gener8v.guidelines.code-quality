"""Describe TypeScript and JavaScript classes and interfaces (approximate)."""

from __future__ import annotations

import re

from cq_measure.codebase import Scan
from cq_measure.structure.classes.class_info import ClassInfo
from cq_measure.structure.functions import JavaScriptFunction

_CLASS = re.compile(r"\b(abstract\s+)?class\s+([A-Za-z_$][\w$]*)([^{;]*)\{")
_INTERFACE = re.compile(r"\binterface\s+([A-Za-z_$][\w$]*)([^{;]*)\{")
_EXTENDS = re.compile(r"\bextends\s+([A-Za-z_$][\w$.]*)")
_IMPLEMENTS = re.compile(r"\bimplements\s+(.+)$", re.S)
_INTERFACE_EXTENDS = re.compile(r"\bextends\s+(.+)$", re.S)
_SIGNATURE = re.compile(r"(?m)^\s*(?:readonly\s+)?([A-Za-z_$][\w$]*)\??\s*(?:<[^>()]*>)?\s*\(")
_ABSTRACT_METHOD = re.compile(r"\babstract\s+(?:async\s+)?(?:get\s+|set\s+)?([A-Za-z_$][\w$]*)\s*[(<]")
_GENERICS = re.compile(r"<[^<>]*>")


def javascript_classes(scan: Scan, functions: list[JavaScriptFunction], pairs: dict[int, int]) -> list[ClassInfo]:
    """Return the classes and interfaces declared in the file."""
    found = []
    for match in _CLASS.finditer(scan.code):
        found.append(_class(scan, match, functions, pairs))
    for match in _INTERFACE.finditer(scan.code):
        found.append(_interface(scan, match, pairs))
    return found


def _class(scan: Scan, match: re.Match, functions: list[JavaScriptFunction], pairs: dict[int, int]) -> ClassInfo:
    brace = match.end() - 1
    end = pairs.get(brace, brace)
    header = match.group(3)
    extends = _EXTENDS.search(header)
    implements = _IMPLEMENTS.search(header)
    methods = _top_level_names(functions, brace, end)
    methods += [m.group(1) for m in _ABSTRACT_METHOD.finditer(scan.code, brace, end)]
    return ClassInfo(
        name=match.group(2),
        line=scan.line_of(match.start()),
        kind="abstract" if match.group(1) else "class",
        bases=(extends.group(1).split(".")[-1],) if extends else (),
        implements=_name_list(implements.group(1)) if implements else (),
        methods=tuple(methods),
    )


def _top_level_names(functions: list[JavaScriptFunction], start: int, end: int) -> list[str]:
    names = []
    reach = start
    for function in functions:
        if start < function.body_start < end and function.body_start > reach:
            names.append(function.name)
            reach = function.body_end
    return names


def _interface(scan: Scan, match: re.Match, pairs: dict[int, int]) -> ClassInfo:
    brace = match.end() - 1
    end = pairs.get(brace, brace)
    body = _flatten(scan.code[brace + 1 : end], brace + 1, pairs)
    extends = _INTERFACE_EXTENDS.search(match.group(2))
    return ClassInfo(
        name=match.group(1),
        line=scan.line_of(match.start()),
        kind="interface",
        bases=_name_list(extends.group(1)) if extends else (),
        methods=tuple(m.group(1) for m in _SIGNATURE.finditer(body)),
    )


def _flatten(body: str, offset: int, pairs: dict[int, int]) -> str:
    """Blank nested brace blocks so that only the members at the top level remain."""
    chars = list(body)
    index = 0
    while index < len(chars):
        close = pairs.get(offset + index) if chars[index] == "{" else None
        if close is not None:
            inner = slice(index + 1, close - offset)
            chars[inner] = [char if char == "\n" else " " for char in chars[inner]]
            index = close - offset
        index += 1
    return "".join(chars)


def _name_list(text: str) -> tuple[str, ...]:
    without_generics = text
    while _GENERICS.search(without_generics):
        without_generics = _GENERICS.sub("", without_generics)
    names = (part.strip().split(".")[-1] for part in without_generics.split(","))
    return tuple(name for name in names if re.match(r"^[A-Za-z_$][\w$]*$", name))
