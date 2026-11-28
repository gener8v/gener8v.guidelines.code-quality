"""Classify files by role: test, test support, generated, configuration, CLI entry point."""

from __future__ import annotations

import posixpath
import re

from cq_measure.codebase.globs import matches_any
from cq_measure.codebase.language import SCRIPT_LANGUAGES, family_of, language_of
from cq_measure.codebase.package_roots import parts_of

TEST_DIRS = frozenset({"tests", "test", "__tests__", "spec", "specs"})
SUPPORT_DIRS = frozenset({"testdata", "__fixtures__", "fixtures", "__mocks__", "__snapshots__", "testing"})
SUPPORT_FILE = re.compile(r"^(conftest\.py|test[-_]?utils\..+|setup-?tests\..+|(jest|vitest)\.setup\..+)$", re.I)
GENERATED_DIRS = frozenset({"generated", "gen", "__generated__"})
SCRIPT_DIRS = frozenset({"scripts", "script", "bin", "tools"})
ROUTE_DIRS = frozenset({"app", "pages", "routes"})
FRAMEWORK_STEMS = frozenset(
    "page layout loading error not-found template default route global-error middleware instrumentation "
    "_app _document _error +page +layout +server root".split()
)
TEST_CATEGORIES = frozenset({"integration", "e2e", "unit", "int", "component"})

_PY_TEST = re.compile(r"^(?:test_(?P<a>.+)|(?P<b>.+)_test)\.py$")
_SCRIPT_TEST = re.compile(r"^(?P<a>.+?)\.(?:test|spec)\.[cm]?[jt]sx?$")
_OTHER_TEST = re.compile(r"^(?P<a>.+?)(?:_test\.go|Tests?\.(?:java|kt|cs|swift)|IT\.java|_(?:spec|test)\.rb)$")
_CONFIG_NAME = re.compile(r"(\.config\.[cm]?[jt]s$|rc\.[cm]?js$|^(setup|manage|noxfile|fabfile|conftest)\.py$)")
_MAIN_BLOCK = re.compile(r"^if\s+__name__\s*==\s*['\"]__main__['\"]\s*:", re.M)
_COMMENT_START = r"^\s*(?:#|//|/\*|\*|<!--|\"\"\"|''')"
_GENERATED_MARKER = re.compile(_COMMENT_START + r".*(@generated|DO NOT EDIT|auto-?generated|Code generated)", re.I)


def is_test_file(path: str) -> bool:
    """Return True when the file name marks a unit test (`x_test.py`, `x.test.ts`, ...)."""
    return test_subject(path) is not None or posixpath.basename(path) == "tests.py"


def test_subject(path: str) -> str | None:
    """Return the name of the file that a test file tests, or None for a non-test file."""
    name = posixpath.basename(path)
    for pattern in (_PY_TEST, _SCRIPT_TEST, _OTHER_TEST):
        match = pattern.match(name)
        if match:
            subject = match.group("a") or match.groupdict().get("b")
            return _strip_category(subject)
    return None


def _strip_category(subject: str) -> str:
    parts = subject.split(".")
    while len(parts) > 1 and parts[-1].lower() in TEST_CATEGORIES:
        parts.pop()
    return ".".join(parts)


def in_test_tree(path: str) -> bool:
    """Return True for a file below a test or test-data directory."""
    parts = parts_of(posixpath.dirname(path))
    return any(part in TEST_DIRS or part in SUPPORT_DIRS for part in parts) or "/src/test/" in "/" + path


def is_testish(path: str) -> bool:
    """Return True for a test file, a test support file, or a file in a test tree."""
    return is_test_file(path) or in_test_tree(path) or bool(SUPPORT_FILE.match(posixpath.basename(path)))


def generated_marker_line(lines: list[str]) -> int | None:
    """Return the line of a generated-code marker in the first 10 lines, or None."""
    for number, line in enumerate(lines[:10], start=1):
        if _GENERATED_MARKER.search(line):
            return number
    return None


def in_generated_dir(path: str) -> bool:
    return any(part in GENERATED_DIRS for part in parts_of(posixpath.dirname(path)))


def is_generated(source) -> bool:
    """Return True for a file in a generated directory or with a generated marker."""
    return in_generated_dir(source.path) or generated_marker_line(source.lines) is not None


def is_config_name(name: str) -> bool:
    """Return True for tool configuration such as `vite.config.ts` or `conftest.py`."""
    return name.startswith(".") or bool(_CONFIG_NAME.search(name))


def in_script_dir(path: str) -> bool:
    """Return True below `scripts/`, `bin/`, `tools/`, or a `cli` directory."""
    return any(part in SCRIPT_DIRS or _is_cli_dir(part) for part in parts_of(posixpath.dirname(path)))


def _is_cli_dir(name: str) -> bool:
    return name == "cli" or name.endswith(("-cli", "_cli"))


def is_cli_entry(source) -> bool:
    """Return True for `__main__.py`, a `__main__` block, a shebang, or a file in a script directory."""
    if source.name == "__main__.py" or in_script_dir(source.path):
        return True
    return source.text.startswith("#!") or bool(_MAIN_BLOCK.search(source.text))


def in_route_tree(path: str) -> bool:
    """Return True for a TypeScript or JavaScript file below `app/`, `pages/`, or `routes/`."""
    if language_of(path) not in SCRIPT_LANGUAGES:
        return False
    return any(part in ROUTE_DIRS for part in parts_of(posixpath.dirname(path)))


def is_framework_file(path: str) -> bool:
    """Return True for names that a framework requires, such as Next.js `page.tsx`."""
    stem = posixpath.basename(path).split(".")[0]
    return family_of(language_of(path)) == "script" and stem in FRAMEWORK_STEMS


def is_entry_point(source, patterns) -> bool:
    """Return True for files that a tool or a person runs directly, not through an import."""
    if matches_any(source.path, patterns) or is_config_name(source.name):
        return True
    return is_cli_entry(source) or is_framework_file(source.path)
