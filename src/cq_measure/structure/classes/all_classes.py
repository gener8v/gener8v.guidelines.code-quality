"""Collect the classes and interfaces of a whole repository."""

from __future__ import annotations


def all_classes(workspace) -> list:
    """Return (file, class info) for every class and interface in the repository."""
    return workspace.repository_fact("classes", lambda: [(s, info) for s in workspace.sources for info in workspace.classes(s)])
