"""The measured size and shape of one function."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FunctionMeasure:
    """Lines, nesting, complexity, and parameters of one function or method."""

    name: str
    line: int
    lines: int
    nesting: int
    complexity: int
    params: int
    flag_params: tuple[str, ...] = ()
