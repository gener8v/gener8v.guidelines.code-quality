"""Rule 4.6: keep classes small."""

from __future__ import annotations

from cq_measure.codebase import is_testish
from cq_measure.structure.classes.all_classes import all_classes


def check_class_methods(workspace, emit) -> None:
    for source, info in all_classes(workspace):
        if info.kind == "interface" or is_testish(source.path) or workspace.generated(source):
            continue
        count = len(info.methods)
        text = (f"Class `{info.name}` has {count} methods", "Split it along the groups of fields that the methods use.")
        emit.measure((source.path, info.line), count, text)
