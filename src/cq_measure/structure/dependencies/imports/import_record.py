"""One import statement, and where it resolves in the repository."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ImportRecord:
    """An import as written, plus its resolved target file (None when external)."""

    line: int
    specifier: str
    climb: int = 0
    type_only: bool = False
    names: tuple[str, ...] = ()
    target: str | None = None
