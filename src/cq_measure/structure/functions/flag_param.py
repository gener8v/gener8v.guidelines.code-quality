"""Rule 4.5: do not use a boolean parameter to switch behavior."""

from __future__ import annotations

from cq_measure.codebase import is_testish
from cq_measure.structure.functions.each_function import each_function


def check_flag_param(workspace, emit) -> None:
    for source, function in each_function(workspace):
        if source.language != "python" or is_testish(source.path):
            continue
        for name in function.flag_params:
            emit.flag(
                (source.path, function.line),
                f"`{function.name}` takes the boolean parameter `{name}`. Write two functions, or make it a keyword-only option.",
            )
