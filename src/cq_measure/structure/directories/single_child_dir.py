"""Rule 2.6: do not nest a directory only to hold one directory."""

from __future__ import annotations

from cq_measure.codebase import ROUTE_DIRS, has_hidden_part, parts_of

LONE_CHILD_EXEMPT = frozenset({"src", "cmd"})


def _lone_child_exempt(workspace, path: str) -> bool:
    parts = parts_of(path)
    if not parts or has_hidden_part(path) or parts[-1] in LONE_CHILD_EXEMPT:
        return True
    if "/src/main" in "/" + path or "/src/test" in "/" + path:
        return True
    return any(part in ROUTE_DIRS for part in parts) and _has_javascript_files(workspace, path)


def _has_javascript_files(workspace, path: str) -> bool:
    prefix = path + "/"
    return any(source.path.startswith(prefix) and source.language in ("tsx", "jsx", "typescript", "javascript") for source in workspace.sources)


def check_single_child_dir(workspace, emit) -> None:
    for path, directory in sorted(workspace.directories.items()):
        if directory.files or len(directory.subdirs) != 1 or _lone_child_exempt(workspace, path):
            continue
        child = next(iter(directory.subdirs))
        emit.flag((path, None), f"`{path}` holds only `{child}/`. Move the content up one level.")
