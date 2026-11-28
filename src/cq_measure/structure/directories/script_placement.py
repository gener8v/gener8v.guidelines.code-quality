"""Rule 2.7: give scripts their own directory."""

from __future__ import annotations

from cq_measure.codebase import CODE_LANGUAGES, has_hidden_part, language_of, parts_of

SOURCE_DIR_NAMES = frozenset({"src", "lib", "app", "pkg", "internal"})


def check_script_placement(workspace, emit) -> None:
    script_dirs = set(emit.option("dirs", []))
    for source in workspace.sources:
        if source.language != "shell" or has_hidden_part(source.path):
            continue
        parts = parts_of(source.directory)
        if any(part in script_dirs for part in parts) or not _is_source_dir(workspace, source.directory):
            continue
        emit.flag((source.path, None), "Shell script in a source directory. Move it to `scripts/`, `bin/`, or `tools/`.")


def _is_source_dir(workspace, path: str) -> bool:
    if any(part in SOURCE_DIR_NAMES for part in parts_of(path)):
        return True
    if path in workspace.package_roots:
        return False
    directory = workspace.directories.get(path)
    return bool(directory) and any(language_of(name) in CODE_LANGUAGES for name in directory.files)
