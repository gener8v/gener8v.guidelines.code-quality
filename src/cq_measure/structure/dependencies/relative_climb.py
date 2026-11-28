"""Rule 3.3: do not climb more than two levels in a relative import."""

from __future__ import annotations


def check_relative_climb(workspace, emit) -> None:
    for path, records in sorted(workspace.graph.records.items()):
        for record in records:
            if record.climb:
                text = (f"`{record.specifier}` climbs {record.climb} levels", "Import through the package entry point or a path alias.")
                emit.measure((path, record.line), record.climb, text)
