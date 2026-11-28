"""The directory tree that the discovered files imply."""

from __future__ import annotations

import posixpath
from dataclasses import dataclass, field


@dataclass
class Directory:
    """The file names and subdirectory names directly inside one directory."""

    path: str
    files: list[str] = field(default_factory=list)
    subdirs: set[str] = field(default_factory=set)

    @property
    def name(self) -> str:
        return posixpath.basename(self.path)


def build_directories(paths) -> dict[str, Directory]:
    """Return every directory that holds a discovered file, keyed by path ("" is the root)."""
    tree: dict[str, Directory] = {"": Directory("")}
    for path in paths:
        parent = posixpath.dirname(path)
        _ensure(tree, parent).files.append(posixpath.basename(path))
    return tree


def _ensure(tree: dict[str, Directory], path: str) -> Directory:
    if path in tree:
        return tree[path]
    directory = Directory(path)
    tree[path] = directory
    parent = _ensure(tree, posixpath.dirname(path))
    parent.subdirs.add(posixpath.basename(path))
    return directory


def has_hidden_part(path: str) -> bool:
    """Return True when a part of the path starts with a dot, such as `.github/x`."""
    return any(part.startswith(".") for part in path.split("/") if part)
