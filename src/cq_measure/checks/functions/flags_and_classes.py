"""Rules 4.5 and 4.6: no boolean switch parameters, and small classes."""

from __future__ import annotations

from cq_measure.workspace import all_classes

from cq_measure.checks.functions.function_checks import each_function
from cq_measure.source.roles import is_testish


def check_flag_param(workspace, emit) -> None:
    for source, function in each_function(workspace):
        if source.language != "python" or is_testish(source.path):
            continue
        for name in function.flag_params:
            emit.flag(
                (source.path, function.line),
                f"`{function.name}` takes the boolean parameter `{name}`. Write two functions, or make it a keyword-only option.",
            )


def check_class_methods(workspace, emit) -> None:
    for source, info in all_classes(workspace):
        if info.kind == "interface" or is_testish(source.path) or workspace.generated(source):
            continue
        count = len(info.methods)
        text = (f"Class `{info.name}` has {count} methods", "Split it along the groups of fields that the methods use.")
        emit.measure((source.path, info.line), count, text)
