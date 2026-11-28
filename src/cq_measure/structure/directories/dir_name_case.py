"""Rule 2.8: use the case convention of the language for directory names."""

from __future__ import annotations

import re

from cq_measure.codebase import has_hidden_part, language_of

TOOL_DIRS = re.compile(r"^__\w+__$")


FRAMEWORK_DIR = re.compile(r"^(\[.*\]|\(.*\)|@.+|\+.+|\$.+)$")


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
