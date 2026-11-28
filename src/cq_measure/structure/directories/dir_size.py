"""Rule 2.2: keep each directory small."""

from __future__ import annotations

from cq_measure.codebase import is_testish, language_of
from cq_measure.structure.directories.directory_counts import measured_directories


def _counted_file(directory_path: str, name: str) -> bool:
    path = f"{directory_path}/{name}" if directory_path else name
    return language_of(name) is not None and name != "__init__.py" and not is_testish(path)


def check_dir_files(workspace, emit) -> None:
    for path, directory in measured_directories(workspace):
        count = sum(1 for name in directory.files if _counted_file(path, name))
        text = (f"{count} source files in `{path or '.'}`", "Split it into subdirectories that each name one part of its domain function.")
        emit.measure((path or ".", None), count, text)


def check_dir_subdirs(workspace, emit) -> None:
    for path, directory in measured_directories(workspace):
        count = sum(1 for name in directory.subdirs if not name.startswith(".") and name != "__pycache__")
        text = (f"{count} subdirectories in `{path or '.'}`", "Group them under fewer domain directories.")
        emit.measure((path or ".", None), count, text)
