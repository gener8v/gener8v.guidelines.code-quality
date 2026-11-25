"""Rules 2.5, 2.6, and 2.7: package by feature, no lone subdirectories, scripts and generated code apart."""

from __future__ import annotations

from cq_measure.source.directory import has_hidden_part
from cq_measure.source.language import CODE_LANGUAGES, language_of
from cq_measure.source.packages import parts_of
from cq_measure.source.roles import ROUTE_DIRS, generated_marker_line, in_test_tree, is_testish

SOURCE_DIR_NAMES = frozenset({"src", "lib", "app", "pkg", "internal"})
LONE_CHILD_EXEMPT = frozenset({"src", "cmd"})


def check_package_by_layer(workspace, emit) -> None:
    role_dirs = set(emit.option("role_dirs", []))
    minimum = emit.option("min_role_dirs", 3)
    for path, directory in sorted(workspace.directories.items()):
        if has_hidden_part(path) or in_test_tree(path + "/x"):
            continue
        layers = sorted(directory.subdirs & role_dirs)
        if len(layers) >= minimum:
            names = ", ".join(f"`{name}`" for name in layers)
            emit.flag((path or ".", None), f"Subdirectories {names} are layers. Group the code by feature, then by role inside each feature.")


def _lone_child_exempt(workspace, path: str) -> bool:
    parts = parts_of(path)
    if not parts or has_hidden_part(path) or parts[-1] in LONE_CHILD_EXEMPT:
        return True
    if "/src/main" in "/" + path or "/src/test" in "/" + path:
        return True
    return any(part in ROUTE_DIRS for part in parts) and _has_script_files(workspace, path)


def _has_script_files(workspace, path: str) -> bool:
    prefix = path + "/"
    return any(source.path.startswith(prefix) and source.language in ("tsx", "jsx", "typescript", "javascript") for source in workspace.sources)


def check_single_child_dir(workspace, emit) -> None:
    for path, directory in sorted(workspace.directories.items()):
        if directory.files or len(directory.subdirs) != 1 or _lone_child_exempt(workspace, path):
            continue
        child = next(iter(directory.subdirs))
        emit.flag((path, None), f"`{path}` holds only `{child}/`. Move the content up one level.")


def check_generated_placement(workspace, emit) -> None:
    generated_dirs = set(emit.option("dirs", []))
    for source in workspace.sources:
        if any(part in generated_dirs for part in parts_of(source.directory)) or is_testish(source.path):
            continue
        line = generated_marker_line(source.lines)
        if line is not None:
            emit.flag((source.path, line), "Generated code outside a `generated/` directory. Move it there so nobody edits it by hand.")


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
