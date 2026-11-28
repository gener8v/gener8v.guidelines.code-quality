"""Rule 5.5: do not add layers that only pass calls through."""

from __future__ import annotations

from cq_measure.structure.classes import all_classes


def check_pass_through(workspace, emit) -> None:
    minimum = emit.option("min_methods", 3)
    for source, info in all_classes(workspace):
        forwarding = [name for name in info.methods if name != "__init__"]
        if info.pass_through_field and len(forwarding) >= minimum:
            emit.flag(
                (source.path, info.line),
                f"Every method of `{info.name}` only forwards to `self.{info.pass_through_field}`. Remove the class and call the target directly.",
            )
