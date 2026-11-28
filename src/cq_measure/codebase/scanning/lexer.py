"""Lex C-like source text: blank comments, strings, template literals, and regex literals.

The output keeps every offset and line break, so later passes can match
brackets and keywords on the code alone and still report correct lines.
"""

from __future__ import annotations

import re

from cq_measure.codebase.scanning.comment import Comment
from cq_measure.codebase.scanning.scan import Scan

_TOP = re.compile(r"[\"'`/]")
_NESTED = re.compile(r"[\"'`/{}]")
_TEMPLATE_STOP = re.compile(r"[`\\]|\$\{")
_STRINGS = {
    "'": re.compile(r"'(?:\\[\s\S]|[^'\\\n])*'?"),
    '"': re.compile(r'"(?:\\[\s\S]|[^"\\\n])*"?'),
}
_CHAR_LITERAL = re.compile(r"'(?:\\[^']{1,8}|[^'\\\n])'")
_REGEX_LITERAL = re.compile(r"/(?![*/])(?:\\.|\[(?:\\.|[^\]\\\n])*\]|[^/\\\n\[])+/[A-Za-z]*")
_REGEX_AFTER = frozenset("(,=:[!&|?{};+-*%<>~^")
_REGEX_KEYWORDS = frozenset("return typeof case do else in of new delete void throw yield await instanceof".split())
_LAST_WORD = re.compile(r"[A-Za-z_$][\w$]*\Z")
_NOT_NEWLINE = re.compile(r"[^\n]")


def blank(text: str) -> str:
    """Replace every character except line breaks with a space."""
    return _NOT_NEWLINE.sub(" ", text)


def line_starts(text: str) -> list[int]:
    """Return the offset where each line starts."""
    return [0] + [match.end() for match in re.finditer("\n", text)]


def scan_source(text: str, *, javascript: bool = True) -> Scan:
    """Lex `text`. With `javascript`, a `/` can start a JavaScript regex literal and a backtick a template."""
    lexer = _Lexer(text, javascript)
    lexer.code(nested=False)
    starts = line_starts(text)
    scan = Scan("".join(lexer.out), [], lexer.strings, starts)
    scan.comments = [Comment(scan.line_of(offset) + index, body, own, kind) for offset, index, body, own, kind in lexer.comments]
    return scan


class _Lexer:
    def __init__(self, text: str, javascript: bool):
        self.text = text
        self.javascript = javascript
        self.pos = 0
        self.out: list[str] = []
        self.comments: list[tuple] = []
        self.strings: list[tuple[int, int, str]] = []
        self.hidden = 0

    def emit(self, chunk: str) -> None:
        self.out.append(blank(chunk) if self.hidden else chunk)

    def code(self, *, nested: bool) -> None:
        """Copy code until the end, or until an unmatched `}` when nested in a template."""
        pattern = _NESTED if nested else _TOP
        depth = 0
        while True:
            match = pattern.search(self.text, self.pos)
            if match is None:
                self.emit(self.text[self.pos :])
                self.pos = len(self.text)
                return
            self.emit(self.text[self.pos : match.start()])
            self.pos = match.start()
            char = match.group()
            if char == "}" and depth == 0:
                return
            if char in "{}":
                depth += 1 if char == "{" else -1
                self.emit(char)
                self.pos += 1
            else:
                self.token(char)

    def token(self, char: str) -> None:
        if char == "/":
            self.slash()
        elif char == "`" and self.javascript:
            self.template()
        elif char == "`":
            self.quoted_raw()
        else:
            self.quoted(char)

    def slash(self) -> None:
        following = self.text[self.pos + 1 : self.pos + 2]
        if following == "/":
            self.line_comment()
        elif following == "*":
            self.block_comment()
        elif self.javascript and self.regex_allowed() and self.regex():
            return
        else:
            self.emit("/")
            self.pos += 1

    def line_comment(self) -> None:
        end = self.text.find("\n", self.pos)
        end = len(self.text) if end < 0 else end
        self.comments.append((self.pos, 0, self.text[self.pos + 2 : end].strip(), self.own_line(), "line"))
        self.emit(blank(self.text[self.pos : end]))
        self.pos = end

    def block_comment(self) -> None:
        end = self.text.find("*/", self.pos + 2)
        end = len(self.text) if end < 0 else end + 2
        chunk = self.text[self.pos : end]
        kind = "doc" if chunk.startswith("/**") else "block"
        own = self.own_line()
        for index, raw in enumerate(chunk.split("\n")):
            self.comments.append((self.pos, index, _strip_block(raw), own or index > 0, kind))
        self.emit(blank(chunk))
        self.pos = end

    def own_line(self) -> bool:
        start = self.text.rfind("\n", 0, self.pos) + 1
        return not self.text[start : self.pos].strip()

    def regex_allowed(self) -> bool:
        previous = self.previous_code()
        if not previous or previous[-1] in _REGEX_AFTER:
            return True
        word = _LAST_WORD.search(previous)
        return bool(word) and word.group() in _REGEX_KEYWORDS

    def previous_code(self) -> str:
        for chunk in reversed(self.out):
            stripped = chunk.rstrip()
            if stripped:
                return stripped[-40:]
        return ""

    def regex(self) -> bool:
        match = _REGEX_LITERAL.match(self.text, self.pos)
        if match is None:
            return False
        self.emit("/" + blank(match.group()[1:]))
        self.pos = match.end()
        return True

    def quoted(self, quote: str) -> None:
        if quote == "'" and not self.javascript and not _CHAR_LITERAL.match(self.text, self.pos):
            self.emit("'")
            self.pos += 1
            return
        match = _STRINGS[quote].match(self.text, self.pos)
        literal = match.group()
        closed = len(literal) > 1 and literal.endswith(quote)
        inner = literal[1:-1] if closed else literal[1:]
        self.strings.append((self.pos, match.end(), inner))
        self.emit(quote + blank(inner) + (quote if closed else ""))
        self.pos = match.end()

    def quoted_raw(self) -> None:
        end = self.text.find("`", self.pos + 1)
        end = len(self.text) if end < 0 else end + 1
        self.emit("`" + blank(self.text[self.pos + 1 : end]))
        self.pos = end

    def template(self) -> None:
        self.out.append("`")
        self.pos += 1
        self.hidden += 1
        while self.pos < len(self.text):
            match = _TEMPLATE_STOP.search(self.text, self.pos)
            if match is None:
                self.emit(self.text[self.pos :])
                self.pos = len(self.text)
                break
            self.emit(self.text[self.pos : match.start()])
            self.pos = match.start()
            if self.template_part(match.group()):
                break
        self.hidden -= 1

    def template_part(self, stop: str) -> bool:
        """Consume one escape, `${...}` expression, or the closing backtick. True at the end."""
        if stop == "`":
            self.out.append("`")
            self.pos += 1
            return True
        if stop == "\\":
            self.emit(self.text[self.pos : self.pos + 2])
            self.pos += 2
            return False
        self.emit("${")
        self.pos += 2
        self.code(nested=True)
        if self.pos < len(self.text):
            self.emit("}")
            self.pos += 1
        return False


def _strip_block(raw: str) -> str:
    text = raw.strip()
    for marker in ("/**", "/*"):
        if text.startswith(marker):
            text = text[len(marker) :]
            break
    if text.endswith("*/"):
        text = text[:-2]
    text = text.strip()
    if text.startswith("*"):
        text = text[1:]
    return text.strip()
