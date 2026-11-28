"""Rule 2.3: keep the directory tree shallow."""

from __future__ import annotations

from cq_measure.codebase import language_of, nearest_root, parts_of
from cq_measure.structure.directories.directory_counts import measured_directories

JVM_SOURCE_ROOTS = ("src/main/java", "src/test/java", "src/main/kotlin", "src/test/kotlin")


def depth_of(path: str, roots: set[str]) -> int:
    """Count directory levels below the nearest package root, or below a Java or Kotlin source root."""
    for marker in JVM_SOURCE_ROOTS:
        index = ("/" + path + "/").find("/" + marker + "/")
        if index >= 0:
            return len(parts_of(path[index + len(marker) + 1 :].strip("/")))
    root = nearest_root(path, roots)
    return len(parts_of(path)) - len(parts_of(root))


def check_dir_depth(workspace, emit) -> None:
    for path, directory in measured_directories(workspace):
        if not any(language_of(name) for name in directory.files):
            continue
        depth = depth_of(path, workspace.package_roots)
        text = (f"`{path}` is {depth} levels below its package root", "Flatten the tree: a domain function, one or two subdomains, then a role, are enough.")
        emit.measure((path, None), depth, text)
