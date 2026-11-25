"""Rule 6.4: give each source file that holds logic a test next to it."""

from __future__ import annotations

import posixpath
import re

from cq_measure.checks.files.concepts import normalize
from cq_measure.checks.placement.colocation import subject_dirs
from cq_measure.metrics.python_metrics import has_logic
from cq_measure.source.language import SCRIPT_LANGUAGES, family_of, is_declaration
from cq_measure.source.roles import (
    is_config_name,
    is_framework_file,
    is_test_file,
    is_testish,
    test_subject,
)

EXEMPT_STEMS = frozenset({"__init__", "__main__", "index", "main", "conftest", "setup", "manage"})
_GO_FUNCTION = re.compile(r"^func\s", re.M)


def tested_subjects(workspace) -> set[tuple[str, str]]:
    """Return (directory, normalized subject) for every test file."""
    found = set()
    for source in workspace.sources:
        subject = test_subject(source.path) if is_test_file(source.path) else None
        if subject:
            found.update((directory, normalize(subject)) for directory in subject_dirs(source.path))
    return found


def holds_logic(workspace, source) -> bool:
    """Return True for a file with functions or methods, not only declarations."""
    if source.language == "python":
        tree = workspace.python_tree(source)
        return bool(tree) and has_logic(tree)
    if source.language in SCRIPT_LANGUAGES:
        return bool(workspace.functions(source))
    if source.language == "go":
        return bool(_GO_FUNCTION.search(source.text))
    return False


def _exempt(workspace, source) -> bool:
    if family_of(source.language) not in ("python", "script", "go") or is_testish(source.path):
        return True
    if source.stem in EXEMPT_STEMS or is_config_name(source.name) or is_framework_file(source.path):
        return True
    if is_declaration(source.path) or ".stories." in source.name or "migrations" in source.path.split("/"):
        return True
    return workspace.generated(source)


def check_untested_file(workspace, emit) -> None:
    tested = tested_subjects(workspace)
    for source in workspace.sources:
        if _exempt(workspace, source) or (source.directory, normalize(source.stem)) in tested:
            continue
        if holds_logic(workspace, source):
            emit.flag((source.path, None), f"Holds logic but has no test next to it. Add `{_test_name(source)}`.")


def _test_name(source) -> str:
    if source.language == "python":
        return f"{source.stem}_test.py"
    if source.language == "go":
        return f"{source.stem}_test.go"
    return f"{source.stem}.test{posixpath.splitext(source.name)[1]}"
