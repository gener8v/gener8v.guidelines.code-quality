"""Rules 2.4 and 2.8: no junk-drawer names, and lowercase directory names."""

from __future__ import annotations

import re

from cq_measure.source.directory import has_hidden_part
from cq_measure.source.language import language_of
from cq_measure.source.packages import parts_of
from cq_measure.source.roles import ROUTE_DIRS, is_test_file

# Junk-drawer names. None of them names a feature or a category. A repository
# can add names with `vague_names` in .code-quality.json, but it cannot remove these.
VAGUE_NAMES = frozenset(
    "utils util helpers helper misc common stuff general other temp tmp new old".split()
)
# A route directory name is part of a URL, not a grouping of code: `app/projects/new/`.
ROUTE_WORDS = frozenset({"new", "old", "other", "general", "edit"})
DIGIT_WORDS = frozenset(
    "oauth http https base python auth ipv4 ecma html react angular next bcrypt argon scrypt keccak blake "
    "llama gemma mistral qwen claude sonnet opus haiku vite node phi gpt".split()
)
TOOL_DIRS = re.compile(r"^__\w+__$")
FRAMEWORK_DIR = re.compile(r"^(\[.*\]|\(.*\)|@.+|\+.+|\$.+)$")
_COPY_SUFFIX = re.compile(r"[-_. ](old|new|copy)$", re.I)
_DIGIT_SUFFIX = re.compile(r"(?:^|[-_.])([A-Za-z]+)(\d+)$")
SNAKE_DIR = re.compile(r"^_?[a-z0-9]+(?:_[a-z0-9]+)*$")
KEBAB_DIR = re.compile(r"^_?[a-z0-9]+(?:-[a-z0-9]+)*$")
SNAKE_ONLY = frozenset({"python", "rust"})
SNAKE_ALLOWED = frozenset({"python", "rust", "ruby", "go"})


def vague_reason(name: str, vague: set[str]) -> str | None:
    """Return why a name is vague, or None."""
    plain = name.lstrip("_").lower()
    if plain in vague:
        return f"`{name}` is a junk-drawer name"
    if _COPY_SUFFIX.search(name):
        return f"`{name}` ends in a version marker"
    match = _DIGIT_SUFFIX.search(name)
    if match and len(match.group(1)) >= 4 and match.group(1).lower() not in DIGIT_WORDS:
        return f"`{name}` ends in a number"
    return None


def _in_route_tree(path: str) -> bool:
    return any(part in ROUTE_DIRS for part in parts_of(path)[:-1])


def check_vague_name(workspace, emit) -> None:
    vague = VAGUE_NAMES | {name.lower() for name in workspace.config["vague_names"]}
    for path in sorted(workspace.directories):
        if path and not has_hidden_part(path):
            _flag_vague(emit, (path, path + "/x"), "Directory", vague)
    for source in workspace.sources:
        if not is_test_file(source.path) and not has_hidden_part(source.path):
            _flag_vague(emit, (source.path, source.path), "File", vague)


def _flag_vague(emit, paths: tuple[str, str], kind: str, vague: set[str]) -> None:
    """Flag the last name of `paths[0]`. `paths[1]` is the path used for the route-tree test."""
    path, route_probe = paths
    name = path.rsplit("/", 1)[-1]
    if kind == "File":
        name = name.split(".")[0]
    reason = vague_reason(name, vague)
    if reason and not (name.lower() in ROUTE_WORDS and _in_route_tree(route_probe)):
        emit.flag((path, None), f"{kind} {reason}. Name it for the feature or category it holds.")


def _skip_case(path: str, name: str) -> bool:
    if TOOL_DIRS.match(name) or FRAMEWORK_DIR.match(name):
        return True
    return "/src/main/" in "/" + path + "/" or "/src/test/" in "/" + path + "/"


def _languages(directory) -> set[str]:
    return {language_of(name) for name in directory.files} - {None}


def check_dir_name_case(workspace, emit) -> None:
    for path, directory in sorted(workspace.directories.items()):
        if not path or has_hidden_part(path):
            continue
        name = directory.name
        if _skip_case(path, name):
            continue
        languages = _languages(directory)
        if languages & SNAKE_ONLY:
            expected, ok = "snake_case (Python cannot import a name with a hyphen)", SNAKE_DIR.match(name)
        elif languages & SNAKE_ALLOWED:
            expected, ok = "lowercase snake_case or kebab-case", SNAKE_DIR.match(name) or KEBAB_DIR.match(name)
        else:
            expected, ok = "lowercase kebab-case", KEBAB_DIR.match(name)
        if not ok:
            emit.flag((path, None), f"Directory `{name}` is not {expected}. Rename it.")
