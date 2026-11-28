"""A file of the repository and its text, read on first use."""

from __future__ import annotations

import posixpath
from functools import cached_property
from pathlib import Path

from cq_measure.codebase.language import language_of, stem_of


class SourceFile:
    """A discovered file. `path` is relative to the repository root, with `/`."""

    def __init__(self, root: Path, path: str):
        self.root = root
        self.path = path
        self.language = language_of(path)

    def __repr__(self) -> str:
        return f"SourceFile({self.path!r})"

    @property
    def name(self) -> str:
        return posixpath.basename(self.path)

    @property
    def stem(self) -> str:
        return stem_of(self.path)

    @property
    def directory(self) -> str:
        return posixpath.dirname(self.path)

    @cached_property
    def text(self) -> str:
        return (self.root / self.path).read_text(encoding="utf-8", errors="replace")

    @cached_property
    def lines(self) -> list[str]:
        return self.text.splitlines()

    @cached_property
    def nonblank(self) -> int:
        return sum(1 for line in self.lines if line.strip())
