"""Rule 4.1: keep functions short."""

from __future__ import annotations

from cq_measure.structure.functions.each_function import each_function

SUITE_CALLBACKS = frozenset({"describe callback", "describe.each callback", "context callback", "suite callback"})


def check_function_lines(workspace, emit) -> None:
    for source, function in each_function(workspace):
        if function.name in SUITE_CALLBACKS:
            continue
        text = (f"`{function.name}` is {function.lines} lines long", "Extract each step into a function named for what it does.")
        emit.measure((source.path, function.line), function.lines, text)
