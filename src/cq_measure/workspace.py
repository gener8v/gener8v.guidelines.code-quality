"""Everything the checks read about one repository, computed once and shared."""

from __future__ import annotations

import ast
import re
import warnings
from collections import Counter
from functools import cached_property
from pathlib import Path

from cq_measure.codebase import (
    JAVASCRIPT_LANGUAGES,
    CompilerResult,
    SourceFile,
    build_directories,
    comments_of,
    discover,
    is_generated,
    measure_with_compiler,
    package_roots,
    scan_source,
)
from cq_measure.structure.classes import classes_of
from cq_measure.structure.dependencies import (
    ModuleGraph,
    build_graph,
    javascript_exports,
)
from cq_measure.structure.functions import functions_of

_IDENTIFIER = re.compile(r"[A-Za-z_$][\w$]*")


class Workspace:
    """The files of one repository and the facts derived from them, cached per file."""

    def __init__(self, root: Path, config: dict, paths: list[str]):
        self.root = root
        self.config = config
        self.files = [SourceFile(root, path) for path in paths]
        self.by_path = {source.path: source for source in self.files}
        self._memo: dict[tuple[str, str], object] = {}

    @cached_property
    def sources(self) -> list[SourceFile]:
        """Files in a programming language (shell scripts included)."""
        return [source for source in self.files if source.language]

    @cached_property
    def package_roots(self) -> set[str]:
        return package_roots(self.by_path)

    @cached_property
    def directories(self) -> dict:
        return build_directories(self.by_path)

    @cached_property
    def graph(self) -> ModuleGraph:
        return build_graph(self)

    def cached(self, kind: str, source: SourceFile, compute):
        key = (kind, source.path)
        if key not in self._memo:
            self._memo[key] = compute(source)
        return self._memo[key]

    def repository_fact(self, kind: str, compute=None):
        """Compute a fact about the whole repository once.

        Without `compute`, return the fact if it is already known, or None.
        """
        key = (kind, "")
        if key not in self._memo and compute is not None:
            self._memo[key] = compute()
        return self._memo.get(key)

    def generated(self, source: SourceFile) -> bool:
        return self.cached("generated", source, is_generated)

    def python_tree(self, source: SourceFile) -> ast.Module | None:
        return self.cached("ast", source, _parse_python)

    def scan(self, source: SourceFile):
        return self.cached("scan", source, lambda s: scan_source(s.text, javascript=s.language in JAVASCRIPT_LANGUAGES))

    def comments(self, source: SourceFile) -> list:
        return self.cached("comments", source, lambda s: comments_of(s, self.scan))

    def functions(self, source: SourceFile) -> list:
        """Return the function measures of a Python, TypeScript, or JavaScript file."""
        return self.cached("functions", source, lambda s: functions_of(s, self.python_tree(s), self.scan, compiled_for(self, s)))

    def classes(self, source: SourceFile) -> list:
        """Return the classes (and TypeScript interfaces) of a file."""
        return self.cached("classes", source, lambda s: classes_of(s, self.python_tree(s), self.scan, compiled_for(self, s)))

    def exports(self, source: SourceFile) -> list:
        """Return the exports of a TypeScript or JavaScript file."""
        jsx = source.language in ("tsx", "jsx")
        return self.cached("exports", source, lambda s: javascript_exports(self.scan(s), jsx=jsx))

    @cached_property
    def mentions(self) -> Counter:
        """Count, for each identifier, the number of files whose text contains it."""
        counts: Counter = Counter()
        for source in self.files:
            counts.update(set(_IDENTIFIER.findall(source.text)))
        return counts


def load_workspace(root: Path, config: dict) -> Workspace:
    """Discover the files under `root` and wrap them in a workspace."""
    return Workspace(root, config, discover(root, config["ignore"]))


def compiled_for(workspace: Workspace, source: SourceFile) -> CompilerResult | None:
    """Return the compiler measures for a TypeScript or JavaScript file, or None for other languages.

    The first call measures every TypeScript and JavaScript file of the repository at once.
    """
    if source.language not in JAVASCRIPT_LANGUAGES:
        return None
    return workspace.repository_fact("typescript", lambda: measure_with_compiler(workspace.root, _javascript_paths(workspace)))


def _javascript_paths(workspace: Workspace) -> list[str]:
    return [source.path for source in workspace.sources if source.language in JAVASCRIPT_LANGUAGES]


def typescript_status(workspace: Workspace) -> dict | None:
    """Say how the TypeScript and JavaScript functions were measured, or None when no check measured them."""
    compiled = workspace.repository_fact("typescript")
    return compiled.status if compiled is not None else None


def _parse_python(source: SourceFile) -> ast.Module | None:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", SyntaxWarning)
        try:
            return ast.parse(source.text, filename=source.path)
        except (SyntaxError, ValueError):
            return None
