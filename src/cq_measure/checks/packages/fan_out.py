"""Rule 3.6: limit the number of repository files that one file imports."""

from __future__ import annotations

from cq_measure.source.language import stem_of

ENTRY_STEMS = frozenset({"index", "__init__"})


def check_fan_out(workspace, emit) -> None:
    for path, targets in sorted(workspace.graph.edges.items()):
        if stem_of(path) in ENTRY_STEMS:
            continue
        count = len(targets)
        text = (f"Imports {count} files of this repository", "Split it so that each part depends on fewer modules.")
        emit.measure((path, None), count, text)
