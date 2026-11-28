"""Rule 2.1: keep the repository root (and each package root) clean."""

from __future__ import annotations

from cq_measure.codebase import CODE_LANGUAGES, language_of, matches_any


def check_root_files(workspace, emit) -> None:
    for root in sorted(workspace.package_roots):
        directory = workspace.directories.get(root)
        if directory is None:
            continue
        count = sum(1 for name in directory.files if not name.startswith("."))
        text = (f"{count} files in the root of `{root or '.'}`", "Move source and stray files into directories.")
        emit.measure((root or ".", None), count, text)


def check_root_source(workspace, emit) -> None:
    allowed = emit.option("allow", [])
    for root in sorted(workspace.package_roots):
        directory = workspace.directories.get(root)
        if directory is None:
            continue
        for name in sorted(directory.files):
            language = language_of(name)
            if language not in CODE_LANGUAGES or language == "go" or matches_any(name, allowed):
                continue
            path = f"{root}/{name}" if root else name
            emit.flag((path, None), f"Source module `{name}` sits in the package root. Move it into a source directory.")
