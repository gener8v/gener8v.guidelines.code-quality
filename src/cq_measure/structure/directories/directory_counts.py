"""Count what a directory holds."""

from __future__ import annotations

from cq_measure.codebase import GENERATED_DIRS, has_hidden_part, parts_of


def measured_directories(workspace):
    for path, directory in sorted(workspace.directories.items()):
        if has_hidden_part(path) or any(part in GENERATED_DIRS for part in parts_of(path)):
            continue
        yield path, directory
