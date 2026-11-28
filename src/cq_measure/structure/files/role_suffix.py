"""Rule 1.4: spell each role suffix one way in the whole repository."""

from __future__ import annotations

import re
from collections import defaultdict

from cq_measure.codebase import family_of
from cq_measure.structure.files.file_name_parts import core_name

STYLE_LABELS = {"dot": "`.`", "hyphen": "`-`", "underscore": "`_`", "joined": "joined words"}


_WORDS = re.compile(r"[A-Z]+(?![a-z])|[A-Z]?[a-z0-9]+")


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
