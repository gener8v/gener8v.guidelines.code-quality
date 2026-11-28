"""One comment line found in a source file."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Comment:
    """A comment line: its number, its text without markers, and its kind."""

    line: int
    text: str
    own_line: bool
    kind: str = "line"
