"""Rule 4.2: keep nesting shallow."""

from __future__ import annotations

from cq_measure.structure.functions.each_function import each_function


def check_nesting(workspace, emit) -> None:
    for source, function in each_function(workspace):
        text = (f"`{function.name}` nests blocks {function.nesting} deep", "Return early for the invalid cases and extract inner loops.")
        emit.measure((source.path, function.line), function.nesting, text)
