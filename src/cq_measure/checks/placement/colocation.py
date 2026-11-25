"""Rules 6.1 and 6.2: a unit test sits next to its subject and is named for it."""

from __future__ import annotations

import posixpath
from collections import defaultdict

from cq_measure.checks.files.concepts import normalize
from cq_measure.source.language import family_of
from cq_measure.source.packages import parts_of
from cq_measure.source.roles import is_test_file, is_testish, test_subject

MEASURED_FAMILIES = frozenset({"python", "script", "go", "jvm", "ruby"})
MAX_CANDIDATES = 3
GRAPH_LANGUAGES = frozenset({"python", "typescript", "tsx", "javascript", "jsx"})


def subject_index(workspace) -> dict[tuple[str, str], list[str]]:
    """Map (language family, normalized stem) to the non-test source files with that stem."""
    index: dict[tuple[str, str], list[str]] = defaultdict(list)
    for source in workspace.sources:
        if not is_testish(source.path):
            index[(family_of(source.language), normalize(source.stem))].append(source.path)
    return index


def subject_dirs(test_path: str) -> list[str]:
    """Return the directories where the subject of a test may sit."""
    directory = posixpath.dirname(test_path)
    found = [directory]
    if posixpath.basename(directory) == "__tests__":
        found.append(posixpath.dirname(directory))
    if "/src/test/" in "/" + test_path:
        found.append(("/" + directory).replace("/src/test/", "/src/main/", 1).lstrip("/"))
    return found


def _unit_tests(workspace):
    cross_cutting = set(workspace.config["cross_cutting_test_dirs"])
    for source in workspace.sources:
        family = family_of(source.language)
        if family not in MEASURED_FAMILIES or not is_test_file(source.path):
            continue
        if any(part in cross_cutting for part in parts_of(source.directory)):
            continue
        subject = test_subject(source.path)
        if subject:
            yield source, family, subject


def _placement(workspace, index):
    """Yield (test, subject name, paths elsewhere) for each test without a subject beside it."""
    for source, family, subject in _unit_tests(workspace):
        key = normalize(subject)
        candidates = index.get((family, key), [])
        here = subject_dirs(source.path)
        if any(posixpath.dirname(path) in here for path in candidates):
            continue
        if any(_has_subdir(workspace, directory, key) for directory in here):
            continue
        imported = workspace.graph.edges.get(source.path, {})
        yield source, subject, [path for path in candidates if path in imported or source.language not in GRAPH_LANGUAGES]


def _has_subdir(workspace, directory: str, subject: str) -> bool:
    entry = workspace.directories.get(directory)
    return bool(entry) and any(normalize(name) == subject for name in entry.subdirs)


def check_test_colocation(workspace, emit) -> None:
    for source, _subject, candidates in _placement(workspace, subject_index(workspace)):
        if 1 <= len(candidates) <= MAX_CANDIDATES:
            emit.flag((source.path, None), f"Tests `{candidates[0]}`, which is in another directory. Move the test next to it.")


def check_test_name(workspace, emit) -> None:
    for source, subject, candidates in _placement(workspace, subject_index(workspace)):
        if not candidates:
            emit.flag(
                (source.path, None),
                f"No source file named `{subject}` is next to this test. Name it for the file it tests, or move it to a cross-cutting test directory.",
            )
