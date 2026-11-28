"""Rule 3.4: keep dependencies pointing inward."""

from __future__ import annotations

import posixpath

from cq_measure.codebase import is_testish, parts_of


def layer_violation(importer: str, target: str, layers: dict) -> tuple[str, str] | None:
    """Return (inner name, outer name) when inner code imports outer code, below their common directory."""
    importer_parts, target_parts = _below_common(parts_of(posixpath.dirname(importer)), parts_of(posixpath.dirname(target)))
    inner = [part for part in importer_parts if part in layers["inner"]]
    outer = [part for part in target_parts if part in layers["outer"]]
    if inner and outer and not any(part in layers["outer"] for part in importer_parts):
        return inner[0], outer[0]
    return None


def _below_common(first: list[str], second: list[str]) -> tuple[list[str], list[str]]:
    shared = 0
    while shared < min(len(first), len(second)) and first[shared] == second[shared]:
        shared += 1
    return first[shared:], second[shared:]


def check_layer_direction(workspace, emit) -> None:
    layers = workspace.config["layers"]
    for path, targets in sorted(workspace.graph.edges.items()):
        if is_testish(path):
            continue
        for target, record in sorted(targets.items()):
            violation = layer_violation(path, target, layers)
            if violation:
                inner, outer = violation
                emit.flag((path, record.line), f"`{inner}` code imports `{target}` from the outer layer `{outer}`. Define an interface in `{inner}` and implement it outside.")
