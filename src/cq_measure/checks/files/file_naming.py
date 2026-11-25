"""Rules 1.4 and 1.5: one spelling per role suffix, and one case convention per language."""

from __future__ import annotations

import re
from collections import defaultdict

from cq_measure.source.language import family_of
from cq_measure.source.roles import is_framework_file, is_test_file, test_subject

CASES = {
    "snake": re.compile(r"^[a-z0-9]+(?:_[a-z0-9]+)*$"),
    "kebab": re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$"),
    "pascal": re.compile(r"^[A-Z][A-Za-z0-9]*$"),
    "camel": re.compile(r"^[a-z][A-Za-z0-9]*$"),
}
CASE_LABELS = {"snake": "snake_case", "kebab": "kebab-case", "pascal": "PascalCase", "camel": "camelCase"}
STANDARD_STEMS = frozenset({"__init__", "__main__", "index", "package-info", "module-info", "conftest"})
STYLE_LABELS = {"dot": "`.`", "hyphen": "`-`", "underscore": "`_`", "joined": "joined words"}
_SKIPPED_PARTS = frozenset({"test", "spec", "d", "stories", "config", "setup", "e2e", "integration", "unit"})
_WORDS = re.compile(r"[A-Z]+(?![a-z])|[A-Z]?[a-z0-9]+")


def core_name(source) -> str:
    """Return the stem without test markers: `invoice_test.py` gives `invoice`."""
    subject = test_subject(source.path) if is_test_file(source.path) else None
    return subject or source.stem


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


def role_of(core: str) -> tuple[str, str] | None:
    """Return (last word, separator style) of a name with two or more words."""
    for separator, style in ((".", "dot"), ("-", "hyphen"), ("_", "underscore")):
        if separator in core.strip(separator):
            return core.rsplit(separator, 1)[1].lower(), style
    words = _WORDS.findall(core)
    return (words[-1].lower(), "joined") if len(words) > 1 else None


def check_role_suffix(workspace, emit) -> None:
    roles = workspace.config["role_words"]
    abbreviations = {abbr: role for role, abbrs in roles.items() for abbr in abbrs}
    styles: dict[tuple, dict[str, list]] = defaultdict(lambda: defaultdict(list))
    for source in workspace.sources:
        found = role_of(core_name(source))
        if found is None:
            continue
        word, style = found
        if word in abbreviations:
            emit.flag((source.path, None), f"`{word}` abbreviates the role `{abbreviations[word]}`. Spell the role out in the file name.")
        elif word in roles:
            styles[(family_of(source.language), word)][style].append(source.path)
    for (_family, role), by_style in sorted(styles.items()):
        _report_mixed_styles(emit, role, by_style)


def _report_mixed_styles(emit, role: str, by_style: dict[str, list]) -> None:
    if len(by_style) < 2:
        return
    majority = max(sorted(by_style), key=lambda style: len(by_style[style]))
    count = len(by_style[majority])
    for style, paths in sorted(by_style.items()):
        if style == majority:
            continue
        for path in paths:
            message = (
                f"The role `{role}` is joined with {STYLE_LABELS[style]} here, but with {STYLE_LABELS[majority]} "
                f"in {count} other files. Use one spelling for the role."
            )
            emit.flag((path, None), message)
