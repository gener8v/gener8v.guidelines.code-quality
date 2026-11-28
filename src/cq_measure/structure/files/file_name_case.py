"""Rule 1.5: use one case convention for file names in each language."""

from __future__ import annotations

import re

from cq_measure.codebase import is_framework_file, is_test_file
from cq_measure.structure.files.file_name_parts import core_name

CASES = {
    "snake": re.compile(r"^[a-z0-9]+(?:_[a-z0-9]+)*$"),
    "kebab": re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$"),
    "pascal": re.compile(r"^[A-Z][A-Za-z0-9]*$"),
    "camel": re.compile(r"^[a-z][A-Za-z0-9]*$"),
}


CASE_LABELS = {"snake": "snake_case", "kebab": "kebab-case", "pascal": "PascalCase", "camel": "camelCase"}


STANDARD_STEMS = frozenset({"__init__", "__main__", "index", "package-info", "module-info", "conftest"})


_SKIPPED_PARTS = frozenset({"test", "spec", "d", "stories", "config", "setup", "e2e", "integration", "unit"})


def name_parts(core: str) -> list[str]:
    parts = [part.lstrip("_") for part in core.split(".")]
    return [part for part in parts if part and part.lower() not in _SKIPPED_PARTS]


def _skip_case(source, core: str) -> bool:
    if core in STANDARD_STEMS or is_framework_file(source.path) or source.name.startswith("."):
        return True
    return any(char in core for char in "[]()$+@") or core.startswith("__")


def _tsx_majority(workspace, language: str) -> str:
    counts = {"kebab": 0, "pascal": 0}
    for source in workspace.sources:
        if source.language == language and not _skip_case(source, core_name(source)):
            parts = name_parts(core_name(source))
            for case in counts:
                counts[case] += bool(parts) and all(CASES[case].match(part) for part in parts)
    return "pascal" if counts["pascal"] > counts["kebab"] else "kebab"


def check_file_name_case(workspace, emit) -> None:
    expected_by_language = dict(workspace.config["file_case"])
    for language, case in expected_by_language.items():
        if case == "auto":
            expected_by_language[language] = _tsx_majority(workspace, language)
    for source in workspace.sources:
        expected = expected_by_language.get(source.language)
        core = core_name(source)
        if expected not in CASES or _skip_case(source, core) or is_test_file(source.path):
            continue
        parts = name_parts(core)
        if parts and not all(CASES[expected].match(part) for part in parts):
            label = CASE_LABELS[expected]
            emit.flag((source.path, None), f"`{source.name}` is not {label}. Rename it to match the {label} file names of this language.")
