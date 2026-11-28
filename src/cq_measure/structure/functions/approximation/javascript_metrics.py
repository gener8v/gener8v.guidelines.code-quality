"""Measure TypeScript and JavaScript functions approximately from lexed code.

Complexity counts `if`, loops, `case`, `catch`, `&&`, `||`, `??`, and the
ternary `?`. Nesting counts brace blocks opened by `if`, `else`, loops,
`switch`, `try`, `catch`, and `finally`. Braceless blocks are not counted.
"""

from __future__ import annotations

import re

from cq_measure.codebase import Scan
from cq_measure.structure.functions.approximation.javascript_functions import (
    JavaScriptFunction,
    find_functions,
    match_brackets,
)
from cq_measure.structure.functions.function_measure import FunctionMeasure

_BRANCH = re.compile(r"\b(?:if|for|while|case|catch)\b|&&|\|\||\?\?|\?(?![.?:),=])")
_BRACES = re.compile(r"[{}]")
_WORD_END = re.compile(r"[A-Za-z_$][\w$]*\Z")
CONTROL_HEADERS = frozenset({"if", "for", "while", "switch", "catch", "with", "await"})
CONTROL_WORDS = frozenset({"else", "try", "finally", "do", "catch"})


def measure_javascript(scan: Scan, lines: list[str]) -> list[FunctionMeasure]:
    """Return a measure for every function found in the file."""
    pairs = match_brackets(scan.code)
    functions = find_functions(scan, pairs)
    children = child_functions(functions)
    measurer = _Measurer(scan, pairs, lines)
    return [measurer.measure(function, [functions[i] for i in children[index]]) for index, function in enumerate(functions)]


def child_functions(functions: list[JavaScriptFunction]) -> list[list[int]]:
    """Return, for each function, the indexes of the functions directly inside its body."""
    children: list[list[int]] = [[] for _ in functions]
    stack: list[int] = []
    for index, function in enumerate(functions):
        while stack and not _contains(functions[stack[-1]], function):
            stack.pop()
        if stack:
            children[stack[-1]].append(index)
        stack.append(index)
    return children


def _contains(outer: JavaScriptFunction, inner: JavaScriptFunction) -> bool:
    return outer.body_start < inner.body_start <= outer.body_end


class _Measurer:
    def __init__(self, scan: Scan, pairs: dict[int, int], lines: list[str]):
        self.scan = scan
        self.brackets = (pairs, {close: open_ for open_, close in pairs.items()})
        self.lines = lines

    def measure(self, function: JavaScriptFunction, children: list[JavaScriptFunction]) -> FunctionMeasure:
        if function.body_start == function.body_end:
            return FunctionMeasure(function.name, function.line, 1, 0, 1, function.params)
        code = self.scan.code
        segments = own_segments(function, children)
        text = "".join(code[start:end] for start, end in segments)
        first, last = self.scan.line_of(function.body_start), self.scan.line_of(function.body_end)
        return FunctionMeasure(
            name=function.name,
            line=function.line,
            lines=_body_lines(self.lines, first, last),
            nesting=block_depth(code, self.brackets, segments) if function.block else 0,
            complexity=1 + len(_BRANCH.findall(text)),
            params=function.params,
        )


def own_segments(function: JavaScriptFunction, children: list[JavaScriptFunction]) -> list[tuple[int, int]]:
    """Return the spans of the body that are not inside a nested function's body."""
    segments = []
    position = function.body_start + 1
    for child in children:
        if child.body_start > position:
            segments.append((position, child.body_start))
        position = max(position, child.body_end + 1)
    segments.append((position, function.body_end))
    return segments


def block_depth(code: str, brackets: tuple, segments: list[tuple[int, int]]) -> int:
    """Return the deepest nesting of control-flow brace blocks in the segments."""
    pairs, closers = brackets
    depth = deepest = 0
    stack: list[int] = []
    for start, end in segments:
        for match in _BRACES.finditer(code, start, end):
            if match.group() == "{":
                control = int(is_control_block(code, closers, match.start()))
                stack.append(control)
                depth += control
                deepest = max(deepest, depth)
            elif stack:
                depth -= stack.pop()
    return deepest


def is_control_block(code: str, closers: dict[int, int], brace: int) -> bool:
    """Return True when the brace opens the block of `if`, `else`, a loop, `switch`, or `try`."""
    end = _skip_space_back(code, brace - 1)
    if end < 0:
        return False
    if code[end] == ")" and end in closers:
        header = _skip_space_back(code, closers[end] - 1)
        word = _WORD_END.search(code, max(0, header - 20), header + 1) if header >= 0 else None
        return bool(word) and word.group() in CONTROL_HEADERS
    word = _WORD_END.search(code, max(0, end - 20), end + 1)
    return bool(word) and word.group() in CONTROL_WORDS


def _skip_space_back(code: str, index: int) -> int:
    while index >= 0 and code[index].isspace():
        index -= 1
    return index


def _body_lines(lines: list[str], first: int, last: int) -> int:
    if first == last:
        return 1
    return sum(1 for line in lines[first:last - 1] if line.strip())
