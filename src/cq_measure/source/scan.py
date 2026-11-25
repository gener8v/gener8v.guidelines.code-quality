"""The lexed form of a C-like source file."""

from __future__ import annotations

from bisect import bisect_right
from dataclasses import dataclass, field

from cq_measure.source.comment import Comment


@dataclass
class Scan:
    """Source text with comments, strings, and regex literals blanked out.

    `code` has the same length and line breaks as the original text, so offsets
    and line numbers match. `strings` holds (start, end, value) for each
    quoted string literal.
    """

    code: str
    comments: list[Comment] = field(default_factory=list)
    strings: list[tuple[int, int, str]] = field(default_factory=list)
    line_starts: list[int] = field(default_factory=lambda: [0])

    def line_of(self, offset: int) -> int:
        """Return the 1-based line number of a character offset."""
        return bisect_right(self.line_starts, offset)
