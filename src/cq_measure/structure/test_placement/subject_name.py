"""Rule 6.2: name a test file for the file that it tests."""

from __future__ import annotations

from cq_measure.structure.test_placement.subjects import misplaced_tests, subject_index


def check_test_name(workspace, emit) -> None:
    for source, subject, candidates in misplaced_tests(workspace, subject_index(workspace)):
        if not candidates:
            emit.flag(
                (source.path, None),
                f"No source file named `{subject}` is next to this test. Name it for the file it tests, or move it to a cross-cutting test directory.",
            )
