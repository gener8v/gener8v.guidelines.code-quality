"""Find the file that a test file tests."""

from __future__ import annotations

import posixpath
from collections import defaultdict

from cq_measure.codebase import (
    family_of,
    is_test_file,
    parts_of,
    test_subject,
)
from cq_measure.structure.files import normalize

MEASURED_FAMILIES = frozenset({"python", "javascript", "go", "jvm", "ruby"})


GRAPH_LANGUAGES = frozenset({"python", "typescript", "tsx", "javascript", "jsx"})


def subject_index(workspace) -> dict[tuple[str, str], list[str]]:
    """Map (language family, normalized stem) to the source files with that stem.

    Test support files count, so that the test of a fixture has a subject. Test files do not.
    """
    index: dict[tuple[str, str], list[str]] = defaultdict(list)
    for source in workspace.sources:
        if not is_test_file(source.path):
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


def misplaced_tests(workspace, index):
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
