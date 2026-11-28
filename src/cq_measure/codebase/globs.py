"""Match repository paths against glob patterns with `**` support."""

from __future__ import annotations

import re
from functools import lru_cache


@lru_cache(maxsize=None)
def compile_glob(pattern: str) -> re.Pattern:
    """Compile a glob. A pattern that does not start with `/` matches at any depth."""
    anchored = pattern.startswith("/")
    body = pattern.lstrip("/")
    regex = []
    index = 0
    while index < len(body):
        if body.startswith("**/", index):
            regex.append("(?:.*/)?")
            index += 3
        elif body.startswith("**", index):
            regex.append(".*")
            index += 2
        else:
            regex.append(_translate(body[index]))
            index += 1
    prefix = "" if anchored or body.startswith("**") else "(?:.*/)?"
    return re.compile(prefix + "".join(regex) + r"(?:/.*)?\Z")


def _translate(char: str) -> str:
    if char == "*":
        return "[^/]*"
    if char == "?":
        return "[^/]"
    return re.escape(char)


def matches_any(path: str, patterns) -> bool:
    """Return True when `path` matches one of the glob patterns."""
    return any(compile_glob(pattern).match(path) for pattern in patterns)
