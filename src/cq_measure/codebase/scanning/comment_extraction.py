"""Extract comments from Python and from `#`-comment languages."""

from __future__ import annotations

import io
import re
import tokenize

from cq_measure.codebase.language import C_LIKE_LANGUAGES
from cq_measure.codebase.scanning.comment import Comment

_HASH_LINE = re.compile(r"^\s*#(?!!)(.*)$")


def python_comments(text: str) -> list[Comment]:
    """Return the `#` comments of Python source, found with the tokenizer."""
    try:
        tokens = list(tokenize.generate_tokens(io.StringIO(text).readline))
    except (tokenize.TokenError, SyntaxError):
        return hash_comments(text)
    lines = text.splitlines()
    found = []
    for token in tokens:
        if token.type != tokenize.COMMENT:
            continue
        row, column = token.start
        own = row <= len(lines) and not lines[row - 1][:column].strip()
        found.append(Comment(row, token.string[1:].strip(), own, "line"))
    return found


def hash_comments(text: str) -> list[Comment]:
    """Return full-line `#` comments, skipping a shebang line."""
    found = []
    for number, line in enumerate(text.splitlines(), start=1):
        match = _HASH_LINE.match(line)
        if match:
            found.append(Comment(number, match.group(1).strip(), True, "line"))
    return found


def comments_of(source, scan_of) -> list[Comment]:
    """Return the comments of any source file. `scan_of(source)` lexes C-like languages."""
    if source.language == "python":
        return python_comments(source.text)
    if source.language in C_LIKE_LANGUAGES:
        return scan_of(source).comments
    return hash_comments(source.text) if source.language else []
