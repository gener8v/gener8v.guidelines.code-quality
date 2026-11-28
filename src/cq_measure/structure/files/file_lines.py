"""Rule 1.1: keep each source file short."""

from __future__ import annotations

from cq_measure.codebase import is_testish


def check_file_lines(workspace, emit) -> None:
    for source in workspace.sources:
        if workspace.generated(source):
            continue
        count = source.nonblank
        text = (f"{count} non-blank lines", "Split the file along its concepts.")
        emit.measure((source.path, None), count, text, test=is_testish(source.path))
