"""Rules 5.5 and 5.6: no pass-through layers, and shallow inheritance."""

from __future__ import annotations

from cq_measure.workspace import all_classes

from collections import defaultdict

from cq_measure.source.roles import is_testish

MARKER_BASES = frozenset({"object", "ABC", "Protocol", "Generic", "TypedDict", "NamedTuple"})


def check_pass_through(workspace, emit) -> None:
    minimum = emit.option("min_methods", 3)
    for source, info in all_classes(workspace):
        forwarding = [name for name in info.methods if name != "__init__"]
        if info.pass_through_field and len(forwarding) >= minimum:
            emit.flag(
                (source.path, info.line),
                f"Every method of `{info.name}` only forwards to `self.{info.pass_through_field}`. Remove the class and call the target directly.",
            )


class _Depths:
    def __init__(self, classes):
        self.by_name = defaultdict(list)
        for _source, info in classes:
            if info.kind != "interface":
                self.by_name[info.name].append(info)
        self.memo: dict[int, int] = {}

    def depth(self, info, seen: frozenset = frozenset()) -> int:
        key = id(info)
        if key not in self.memo:
            bases = [base for base in info.bases if base not in MARKER_BASES]
            self.memo[key] = 1 + max((self._base_depth(base, seen | {info.name}) for base in bases), default=-1) if bases else 0
        return self.memo[key]

    def _base_depth(self, base: str, seen: frozenset) -> int:
        candidates = self.by_name.get(base, [])
        if not candidates or base in seen:
            return 0
        return min(self.depth(candidate, seen) for candidate in candidates)


def check_inheritance_depth(workspace, emit) -> None:
    depths = _Depths(all_classes(workspace))
    for source, info in all_classes(workspace):
        if info.kind == "interface" or is_testish(source.path):
            continue
        depth = depths.depth(info)
        text = (f"`{info.name}` is {depth} levels deep in an inheritance chain", "Give the object the parts it needs instead of a parent.")
        emit.measure((source.path, info.line), depth, text)
