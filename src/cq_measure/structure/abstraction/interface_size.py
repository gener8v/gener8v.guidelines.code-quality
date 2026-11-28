"""Rule 5.3: keep interfaces small."""

from __future__ import annotations

from cq_measure.structure.classes import all_classes


def check_interface_size(workspace, emit) -> None:
    for source, info in all_classes(workspace):
        if not info.is_interface:
            continue
        count = len([name for name in info.methods if not name.startswith("__")])
        text = (f"`{info.name}` has {count} methods", "Split it by caller so that no caller depends on methods it does not use.")
        emit.measure((source.path, info.line), count, text)
