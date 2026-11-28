"""Rule 5.1: define an interface only where it has two implementations."""

from __future__ import annotations

import re
from collections import defaultdict

from cq_measure.codebase import SCRIPT_LANGUAGES
from cq_measure.structure.classes import all_classes


def implementations(workspace) -> dict[str, list[str]]:
    """Map each base or interface name to the classes that extend or implement it."""
    found: dict[str, list[str]] = defaultdict(list)
    for _source, info in all_classes(workspace):
        if info.kind == "interface":
            continue
        for name in (*info.bases, *info.implements):
            found[name].append(info.name)
    return found


def structural_uses(workspace, name: str) -> int:
    """Count object literals typed as `name` (`: Name = {`, `satisfies Name`, `as Name`)."""
    pattern = re.compile(rf"(?::\s*{name}\s*=\s*\{{|\bsatisfies\s+{name}\b|\bas\s+{name}\b)")
    return sum(len(pattern.findall(workspace.scan(s).code)) for s in workspace.sources if s.language in SCRIPT_LANGUAGES)


def check_single_implementation(workspace, emit) -> None:
    implementers = implementations(workspace)
    for source, info in all_classes(workspace):
        if not info.is_interface or info.kind == "protocol" or len(implementers[info.name]) != 1:
            continue
        if info.kind == "interface" and structural_uses(workspace, info.name):
            continue
        only = implementers[info.name][0]
        emit.flag(
            (source.path, info.line),
            f"`{info.name}` has one implementation, `{only}`. Use the class directly until a second implementation or a test fake exists.",
        )
