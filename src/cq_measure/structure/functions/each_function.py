"""Walk the measured functions of a repository."""

from __future__ import annotations

from cq_measure.codebase import is_declaration


def each_function(workspace):
    """Yield (file, function measure) for every measured function outside generated code."""
    for source in workspace.sources:
        if workspace.generated(source) or is_declaration(source.path):
            continue
        for function in workspace.functions(source):
            yield source, function
