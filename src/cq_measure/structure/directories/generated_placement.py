"""Rule 2.7: give generated code its own directory."""

from __future__ import annotations

from cq_measure.codebase import generated_marker_line, is_testish, parts_of


def check_generated_placement(workspace, emit) -> None:
    generated_dirs = set(emit.option("dirs", []))
    for source in workspace.sources:
        if any(part in generated_dirs for part in parts_of(source.directory)) or is_testish(source.path):
            continue
        line = generated_marker_line(source.lines)
        if line is not None:
            emit.flag((source.path, line), "Generated code outside a `generated/` directory. Move it there so nobody edits it by hand.")
