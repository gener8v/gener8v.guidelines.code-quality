"""Find package roots: directories that hold a build manifest."""

from __future__ import annotations

import posixpath

MANIFESTS = frozenset(
    {"package.json", "pyproject.toml", "setup.py", "go.mod", "Cargo.toml", "pom.xml", "build.gradle", "build.gradle.kts"}
)


def package_roots(paths) -> set[str]:
    """Return the directories that hold a manifest. The repository root ("") is always one."""
    roots = {""}
    for path in paths:
        if posixpath.basename(path) in MANIFESTS:
            roots.add(posixpath.dirname(path))
    return roots


def nearest_root(directory: str, roots: set[str]) -> str:
    """Return the closest package root at or above `directory`."""
    current = directory
    while current and current not in roots:
        current = posixpath.dirname(current)
    return current


def parts_of(directory: str) -> list[str]:
    """Split a directory path into its names. The root has no names."""
    return directory.split("/") if directory else []


def is_within(path: str, directory: str) -> bool:
    """Return True when `path` is `directory` or below it."""
    return not directory or path == directory or path.startswith(directory + "/")
