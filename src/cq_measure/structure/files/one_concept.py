"""Rule 1.2: put one concept in each file."""

from __future__ import annotations

from cq_measure.structure.files.concept_names import (
    ENTRY_STEMS,
    concepts_of,
    holds_concepts,
)


def check_one_concept(workspace, emit) -> None:
    for source in workspace.sources:
        if not holds_concepts(workspace, source) or source.stem in ENTRY_STEMS:
            continue
        concepts, _values = concepts_of(workspace, source)
        if len(concepts) > 1:
            names = ", ".join(f"`{name}`" for name, _line, _kind in concepts)
            message = f"{len(concepts)} public classes or components ({names}). Move each into its own file."
            emit.flag((source.path, concepts[1][1]), message)
