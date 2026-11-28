"""What the interface and inheritance checks need to know about one class."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ClassInfo:
    """A class, interface, abstract class, ABC, or Protocol.

    `kind` is `class`, `abstract`, `protocol`, or `interface`. `bases` holds
    the simple names of base classes and extended interfaces; `implements`
    holds the TypeScript `implements` list.
    """

    name: str
    line: int
    kind: str = "class"
    bases: tuple[str, ...] = ()
    implements: tuple[str, ...] = ()
    methods: tuple[str, ...] = ()
    top_level: bool = True
    pass_through_field: str | None = None

    @property
    def is_interface(self) -> bool:
        return self.kind in ("abstract", "protocol", "interface")
