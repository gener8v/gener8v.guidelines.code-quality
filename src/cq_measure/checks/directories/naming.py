"""Rules 2.4 and 2.8: no junk-drawer names, and lowercase directory names."""

from __future__ import annotations

import re

from cq_measure.source.directory import has_hidden_part
from cq_measure.source.language import language_of
from cq_measure.source.packages import parts_of
from cq_measure.source.roles import ROUTE_DIRS, is_test_file

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
TOOL_DIRS = re.compile(r"^__\w+__$")
FRAMEWORK_DIR = re.compile(r"^(\[.*\]|\(.*\)|@.+|\+.+|\$.+)$")
_COPY_SUFFIX = re.compile(r"[-_. ](old|new|copy)$", re.I)
_DIGIT_SUFFIX = re.compile(r"(?:^|[-_.])([A-Za-z]+)(\d+)$")
SNAKE_DIR = re.compile(r"^_?[a-z0-9]+(?:_[a-z0-9]+)*$")
KEBAB_DIR = re.compile(r"^_?[a-z0-9]+(?:-[a-z0-9]+)*$")
PASCAL_DOTTED_DIR = re.compile(r"^[A-Z][A-Za-z0-9]*(?:\.[A-Z][A-Za-z0-9]*)*$")
ONE_WORD_DIR = re.compile(r"^[a-z][a-z0-9]*$")
# Directory case per language family, in order of precedence. A directory with
# files of more than one language uses the first rule that applies.
DIRECTORY_CASES = (
    ({"csharp"}, "PascalCase, with dots between namespace parts (`Ordering.Domain`)", (PASCAL_DOTTED_DIR,)),
    ({"java", "kotlin", "go"}, "one lowercase word, with no separators (Java and Go package names)", (ONE_WORD_DIR,)),
    ({"python", "rust"}, "snake_case (Python cannot import a name with a hyphen)", (SNAKE_DIR,)),
    ({"ruby"}, "lowercase snake_case or kebab-case", (SNAKE_DIR, KEBAB_DIR)),
)
DEFAULT_CASE = ("lowercase kebab-case", (KEBAB_DIR,))


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
        expected, patterns = expected_case(_languages(directory))
        if not any(pattern.match(name) for pattern in patterns):
            emit.flag((path, None), f"Directory `{name}` is not {expected}. Rename it.")


def expected_case(languages: set[str]) -> tuple[str, tuple]:
    """Return the description and the patterns of the directory case for the languages of its files."""
    for family, expected, patterns in DIRECTORY_CASES:
        if languages & family:
            return expected, patterns
    return DEFAULT_CASE
