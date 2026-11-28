"""Rule 1.3: name the file for its primary concept."""

from __future__ import annotations

import re

from cq_measure.structure.files.concept_names import (
    ENTRY_STEMS,
    concepts_of,
    holds_concepts,
    normalize,
)

_WORDS = re.compile(r"[A-Z]+(?![a-z])|[A-Z]?[a-z0-9]+")


def check_name_matches_export(workspace, emit) -> None:
    for source in workspace.sources:
        if not holds_concepts(workspace, source):
            continue
        concepts, values = concepts_of(workspace, source)
        if len(concepts) != 1 or values != 1:
            continue
        name, line, kind = concepts[0]
        stem = source.directory.rsplit("/", 1)[-1] if source.stem in ENTRY_STEMS else source.stem
        if stem and normalize(stem) != normalize(name):
            suggestion = suggest_name(name, source)
            emit.flag((source.path, line), f"The file holds one {kind}, `{name}`, but is named `{source.name}`. Rename it to `{suggestion}`.")




def suggest_name(name: str, source) -> str:
    words = [word.lower() for word in _WORDS.findall(name)]
    extension = source.name[len(source.stem) :]
    if source.language == "python":
        return "_".join(words) + extension
    if source.language in ("tsx", "jsx") and source.stem[:1].isupper():
        return name + extension
    return "-".join(words) + extension
