"""Rule 2.4: never give a directory or a file a junk-drawer name."""

from __future__ import annotations

import re

from cq_measure.codebase import ROUTE_DIRS, has_hidden_part, is_test_file, parts_of

# Junk-drawer names. None of them names a domain function. A repository
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


_COPY_SUFFIX = re.compile(r"[-_. ](old|new|copy)$", re.I)


_DIGIT_SUFFIX = re.compile(r"(?:^|[-_.])([A-Za-z]+)(\d+)$")


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
        emit.flag((path, None), f"{kind} {reason}. Name it for the domain function that it holds.")
