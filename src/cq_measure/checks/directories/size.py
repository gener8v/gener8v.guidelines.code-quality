"""Rules 2.2 and 2.3: keep each directory small and the tree shallow."""

from __future__ import annotations

from cq_measure.source.directory import has_hidden_part
from cq_measure.source.language import language_of
from cq_measure.source.packages import nearest_root, parts_of
from cq_measure.source.roles import GENERATED_DIRS, is_testish

JVM_SOURCE_ROOTS = ("src/main/java", "src/test/java", "src/main/kotlin", "src/test/kotlin")


def _measured_directories(workspace):
    for path, directory in sorted(workspace.directories.items()):
        if has_hidden_part(path) or any(part in GENERATED_DIRS for part in parts_of(path)):
            continue
        yield path, directory


def _counted_file(directory_path: str, name: str) -> bool:
    path = f"{directory_path}/{name}" if directory_path else name
    return language_of(name) is not None and name != "__init__.py" and not is_testish(path)


def check_dir_files(workspace, emit) -> None:
    for path, directory in _measured_directories(workspace):
        count = sum(1 for name in directory.files if _counted_file(path, name))
        text = (f"{count} source files in `{path or '.'}`", "Split it into subdirectories that each name one part of its domain function.")
        emit.measure((path or ".", None), count, text)


def check_dir_subdirs(workspace, emit) -> None:
    for path, directory in _measured_directories(workspace):
        count = sum(1 for name in directory.subdirs if not name.startswith(".") and name != "__pycache__")
        text = (f"{count} subdirectories in `{path or '.'}`", "Group them under fewer domain directories.")
        emit.measure((path or ".", None), count, text)


def depth_of(path: str, roots: set[str]) -> int:
    """Count directory levels below the nearest package root, or below a Java or Kotlin source root."""
    for marker in JVM_SOURCE_ROOTS:
        index = ("/" + path + "/").find("/" + marker + "/")
        if index >= 0:
            return len(parts_of(path[index + len(marker) + 1 :].strip("/")))
    root = nearest_root(path, roots)
    return len(parts_of(path)) - len(parts_of(root))


def check_dir_depth(workspace, emit) -> None:
    for path, directory in _measured_directories(workspace):
        if not any(language_of(name) for name in directory.files):
            continue
        depth = depth_of(path, workspace.package_roots)
        text = (f"`{path}` is {depth} levels below its package root", "Flatten the tree: a domain function, one or two subdomains, then a role, are enough.")
        emit.measure((path, None), depth, text)
