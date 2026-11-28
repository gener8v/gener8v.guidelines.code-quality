"""Find the functions of lexed TypeScript and JavaScript.

This is an approximation that works on code with comments, strings, and
regex literals blanked out: it matches brackets, then reads the shape around
each parameter list (`name(...) {`, `(...) => {`, `x => ...`).
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from cq_measure.codebase import Scan

KEYWORDS = frozenset(
    "if for while switch catch with return typeof await else do new yield throw delete void case in of "
    "instanceof import super extends implements".split()
)
_IDENT_END = re.compile(r"[A-Za-z_$][\w$]*\Z")
_SINGLE_ARROW = re.compile(r"(?<![\w$.])([A-Za-z_$][\w$]*)\s*=>")
_ASSIGNED = re.compile(r"([A-Za-z_$][\w$]*)\s*(?::[^=;{}()]{1,80})?=\s*(?:async\s*)?(?:function\b\s*\*?\s*)?\Z")
_PROPERTY = re.compile(r"([A-Za-z_$][\w$]*)\s*:\s*(?:async\s*)?(?:function\b\s*\*?\s*)?\Z")
_CALLBACK = re.compile(r"([A-Za-z_$][\w$.]*)\s*\(\s*(?:[^()]*,\s*)?(?:async\s*)?\Z")
_TYPE_ALIAS_END = re.compile(r"\btype\s+[A-Za-z_$][\w$]*\s*(?:<[^=]*>)?\s*=\s*\Z")
_TYPE_ALIAS = re.compile(r"\btype\s+[A-Za-z_$][\w$]*\s*(?:<[^=]*?>)?\s*=")
_TYPE_BODY = re.compile(r"\b(?:interface\s+[A-Za-z_$][\w$]*[^{;]*|declare\s+(?:module|global|namespace)[^{;]*)\{")
_BRACKETS = re.compile(r"[(){}\[\]]")
_THIS_PARAM = re.compile(r"this\s*:")
_OPENERS = {")": "(", "]": "[", "}": "{"}


@dataclass(frozen=True)
class JavaScriptFunction:
    """A function, method, or arrow function. The body spans `body_start` to `body_end`."""

    name: str
    line: int
    params: int
    body_start: int
    body_end: int
    block: bool


def match_brackets(code: str) -> dict[int, int]:
    """Map each opening bracket offset to its closing offset. Unmatched closers are ignored."""
    pairs: dict[int, int] = {}
    stack: list[tuple[str, int]] = []
    for match in _BRACKETS.finditer(code):
        char, index = match.group(), match.start()
        if char in "({[":
            stack.append((char, index))
        elif stack and stack[-1][0] == _OPENERS[char]:
            pairs[stack.pop()[1]] = index
    return pairs


def find_functions(scan: Scan, pairs: dict[int, int]) -> list[JavaScriptFunction]:
    """Return the functions in source order. Functions inside type declarations are left out."""
    code = scan.code
    found: dict[int, JavaScriptFunction] = {}
    for start, end in pairs.items():
        if code[start] == "(":
            function = _from_parens(scan, pairs, start, end)
            if function:
                found.setdefault(function.body_start, function)
    for match in _SINGLE_ARROW.finditer(code):
        function = _from_single(scan, pairs, match)
        if function:
            found.setdefault(function.body_start, function)
    spans = type_spans(code, pairs)
    kept = [f for f in found.values() if not any(start < f.body_start < end for start, end in spans)]
    return sorted(kept, key=lambda function: function.body_start)


def _from_parens(scan: Scan, pairs: dict[int, int], start: int, end: int) -> JavaScriptFunction | None:
    code = scan.code
    kind, position = _after_params(code, end + 1, pairs)
    params = count_params(code[start + 1 : end])
    if kind == "arrow":
        return _arrow(scan, pairs, start, (position, params))
    if kind != "block" or position not in pairs:
        return None
    name = _definition_name(code, start)
    if name is None:
        return None
    return JavaScriptFunction(name, scan.line_of(start), params, position, pairs[position], True)


def _from_single(scan: Scan, pairs: dict[int, int], match: re.Match) -> JavaScriptFunction | None:
    before = _skip_space_back(scan.code, match.start(1) - 1)
    if before >= 0 and scan.code[before] == ":":
        return None
    return _arrow(scan, pairs, match.start(1), (match.end(), 1))


def _arrow(scan: Scan, pairs: dict[int, int], start: int, body: tuple[int, int]) -> JavaScriptFunction | None:
    code = scan.code
    position, params = body
    prefix = code[max(0, start - 160) : start]
    if _TYPE_ALIAS_END.search(prefix):
        return None
    position = _skip_space(code, position)
    if position >= len(code):
        return None
    if code[position] in "{(" and position in pairs:
        name = _context_name(prefix) or "<anonymous>"
        return JavaScriptFunction(name, scan.line_of(start), params, position, pairs[position], code[position] == "{")
    assigned = _ASSIGNED.search(prefix)
    if assigned is None:
        return None
    return JavaScriptFunction(assigned.group(1), scan.line_of(start), params, position, position, False)


def _after_params(code: str, index: int, pairs: dict[int, int]) -> tuple[str | None, int]:
    position = _skip_space(code, index)
    if position < len(code) and code[position] == ":":
        position = _skip_space(code, _skip_type(code, position + 1, pairs))
    if code.startswith("=>", position):
        return "arrow", position + 2
    if position < len(code) and code[position] == "{":
        return "block", position
    return None, position


def _skip_type(code: str, index: int, pairs: dict[int, int]) -> int:
    """Skip a return type annotation. Stop at the body brace, `=>`, or the end of the signature."""
    position = _skip_space(code, index)
    if position < len(code) and code[position] == "{" and position in pairs:
        position = pairs[position] + 1
    depth = 0
    limit = min(len(code), position + 300)
    while position < limit:
        step = _type_step(code, position, pairs, depth)
        if step is None:
            return position
        position, depth = step
    return position


def _type_step(code: str, position: int, pairs: dict[int, int], depth: int) -> tuple[int, int] | None:
    """Advance over one character or bracket group of a type. Return None at the end of the type."""
    char = code[position]
    if code.startswith("=>", position):
        return None if depth == 0 else (position + 2, depth)
    if char in "([" or (char == "{" and depth > 0):
        return pairs.get(position, position) + 1, depth
    if depth == 0 and char in "{;,)}=":
        return None
    if char == "<":
        return position + 1, depth + 1
    if char == ">":
        return position + 1, max(0, depth - 1)
    return position + 1, depth


def _definition_name(code: str, paren: int) -> str | None:
    match = _name_before(code, paren)
    if match is None:
        return None
    word = match.group()
    if word == "function":
        return _context_name(code[max(0, match.start() - 160) : match.start()]) or "<anonymous>"
    if word in KEYWORDS or _follows_keyword(code, match.start()) or _follows_dot(code, match.start()):
        return None
    return word


def _name_before(code: str, paren: int) -> re.Match | None:
    end = _skip_space_back(code, paren - 1)
    if end >= 0 and code[end] == ">":
        end = _skip_space_back(code, code.rfind("<", max(0, end - 120), end) - 1)
    if end < 0:
        return None
    return _IDENT_END.search(code, max(0, end - 80), end + 1)


def _follows_keyword(code: str, start: int) -> bool:
    previous = _IDENT_END.search(code, max(0, start - 20), _skip_space_back(code, start - 1) + 1)
    return bool(previous) and previous.group() in KEYWORDS


def _follows_dot(code: str, start: int) -> bool:
    before = _skip_space_back(code, start - 1)
    return before >= 0 and code[before] == "."


def _context_name(prefix: str) -> str | None:
    for pattern in (_ASSIGNED, _PROPERTY):
        match = pattern.search(prefix)
        if match:
            return match.group(1)
    match = _CALLBACK.search(prefix)
    return f"{match.group(1)} callback" if match else None


def count_params(text: str) -> int:
    """Count the parameters in a parameter list, ignoring commas inside brackets and generics."""
    stripped = text.strip()
    if not stripped:
        return 0
    depth = 0
    commas = 0
    for index, char in enumerate(stripped):
        depth = max(0, depth + _depth_change(stripped, index))
        commas += char == "," and depth == 0
    count = commas + (0 if stripped.endswith(",") else 1)
    return count - (1 if _THIS_PARAM.match(stripped) else 0)


def _depth_change(text: str, index: int) -> int:
    char = text[index]
    previous = text[index - 1] if index else ""
    if char in "([{" or (char == "<" and (previous.isalnum() or previous in "_$")):
        return 1
    if char in ")]}" or (char == ">" and previous != "="):
        return -1
    return 0


def type_spans(code: str, pairs: dict[int, int]) -> list[tuple[int, int]]:
    """Return the spans of interface bodies, `declare` blocks, and type alias declarations."""
    spans = []
    for match in _TYPE_BODY.finditer(code):
        brace = match.end() - 1
        spans.append((brace, pairs.get(brace, brace)))
    for match in _TYPE_ALIAS.finditer(code):
        spans.append((match.start(), _statement_end(code, match.end(), pairs)))
    return spans


def _statement_end(code: str, index: int, pairs: dict[int, int]) -> int:
    position = index
    limit = min(len(code), index + 5000)
    while position < limit:
        char = code[position]
        if char in "([{" and position in pairs:
            position = pairs[position] + 1
            continue
        if char == ";" or (char == "\n" and position + 1 < len(code) and code[position + 1].isalpha()):
            return position
        position += 1
    return position


def _skip_space(code: str, index: int) -> int:
    while index < len(code) and code[index].isspace():
        index += 1
    return index


def _skip_space_back(code: str, index: int) -> int:
    while index >= 0 and code[index].isspace():
        index -= 1
    return index
