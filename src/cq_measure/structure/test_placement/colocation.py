"""Rule 6.1: put each unit test next to the file that it tests."""

from __future__ import annotations

from cq_measure.structure.test_placement.subjects import misplaced_tests, subject_index

MAX_CANDIDATES = 3


def check_test_colocation(workspace, emit) -> None:
    for source, _subject, candidates in misplaced_tests(workspace, subject_index(workspace)):
        if 1 <= len(candidates) <= MAX_CANDIDATES:
            emit.flag((source.path, None), f"Tests `{candidates[0]}`, which is in another directory. Move the test next to it.")
