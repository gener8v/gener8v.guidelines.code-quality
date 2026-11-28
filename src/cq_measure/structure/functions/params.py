"""Rule 4.4: limit the number of parameters."""

from __future__ import annotations

from cq_measure.structure.functions.each_function import each_function


def check_params(workspace, emit) -> None:
    for source, function in each_function(workspace):
        text = (f"`{function.name}` takes {function.params} parameters", "Group related parameters into one named object.")
        emit.measure((source.path, function.line), function.params, text)
