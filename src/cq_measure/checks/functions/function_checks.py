"""Rules 4.1 to 4.4: short, shallow, simple functions with few parameters."""

from __future__ import annotations

from cq_measure.source.language import is_declaration


def each_function(workspace):
    """Yield (file, function measure) for every measured function outside generated code."""
    for source in workspace.sources:
        if workspace.generated(source) or is_declaration(source.path):
            continue
        for function in workspace.functions(source):
            yield source, function


SUITE_CALLBACKS = frozenset({"describe callback", "describe.each callback", "context callback", "suite callback"})


def check_function_lines(workspace, emit) -> None:
    for source, function in each_function(workspace):
        if function.name in SUITE_CALLBACKS:
            continue
        text = (f"`{function.name}` is {function.lines} lines long", "Extract each step into a function named for what it does.")
        emit.measure((source.path, function.line), function.lines, text)


def check_nesting(workspace, emit) -> None:
    for source, function in each_function(workspace):
        text = (f"`{function.name}` nests blocks {function.nesting} deep", "Return early for the invalid cases and extract inner loops.")
        emit.measure((source.path, function.line), function.nesting, text)


def check_complexity(workspace, emit) -> None:
    for source, function in each_function(workspace):
        text = (f"`{function.name}` has complexity {function.complexity}", "Split the branches into smaller functions.")
        emit.measure((source.path, function.line), function.complexity, text)


def check_params(workspace, emit) -> None:
    for source, function in each_function(workspace):
        text = (f"`{function.name}` takes {function.params} parameters", "Group related parameters into one named object.")
        emit.measure((source.path, function.line), function.params, text)
