"""Rules 5.1, 5.3, and 5.7: interfaces with two implementations, small interfaces, no I/Impl names."""

from __future__ import annotations

from cq_measure.workspace import all_classes

import re
from collections import defaultdict

from cq_measure.source.language import SCRIPT_LANGUAGES

_I_PREFIX = re.compile(r"^I[A-Z][a-z]")


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


def check_interface_size(workspace, emit) -> None:
    for source, info in all_classes(workspace):
        if not info.is_interface:
            continue
        count = len([name for name in info.methods if not name.startswith("__")])
        text = (f"`{info.name}` has {count} methods", "Split it by caller so that no caller depends on methods it does not use.")
        emit.measure((source.path, info.line), count, text)


def check_impl_naming(workspace, emit) -> None:
    for source, info in all_classes(workspace):
        if _I_PREFIX.match(info.name) and info.is_interface:
            emit.flag((source.path, info.line), f"`{info.name}` marks itself as an interface. Name it for its role, without the `I` prefix.")
        elif info.name.endswith("Impl") and len(info.name) > 4:
            emit.flag((source.path, info.line), f"`{info.name}` marks itself as an implementation. Name it for how it works, such as `Postgres...`.")
