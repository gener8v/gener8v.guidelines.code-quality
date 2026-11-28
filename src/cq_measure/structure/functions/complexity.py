"""Rule 4.3: keep each function simple."""

from __future__ import annotations

from cq_measure.structure.functions.each_function import each_function


def check_complexity(workspace, emit) -> None:
    for source, function in each_function(workspace):
        text = (f"`{function.name}` has complexity {function.complexity}", "Split the branches into smaller functions.")
        emit.measure((source.path, function.line), function.complexity, text)
