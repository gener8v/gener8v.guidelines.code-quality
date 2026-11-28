"""Rule 5.7: do not mark names as interfaces or implementations."""

from __future__ import annotations

import re

from cq_measure.structure.classes import all_classes

_I_PREFIX = re.compile(r"^I[A-Z][a-z]")


def check_impl_naming(workspace, emit) -> None:
    for source, info in all_classes(workspace):
        if _I_PREFIX.match(info.name) and info.is_interface:
            emit.flag((source.path, info.line), f"`{info.name}` marks itself as an interface. Name it for its role, without the `I` prefix.")
        elif info.name.endswith("Impl") and len(info.name) > 4:
            emit.flag((source.path, info.line), f"`{info.name}` marks itself as an implementation. Name it for how it works, such as `Postgres...`.")
