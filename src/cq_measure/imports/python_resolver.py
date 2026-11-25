"""Resolve Python imports to repository modules."""

from __future__ import annotations

import posixpath

from cq_measure.imports.import_record import ImportRecord
from cq_measure.imports.python_imports import PythonImport


class PythonResolver:
    """Resolves absolute imports against the root, each `src/`, and each package root."""

    def __init__(self, known: set[str], roots: set[str]):
        self.known = known
        bases = set(roots)
        bases.update(posixpath.join(root, "src") if root else "src" for root in roots)
        bases.update(_src_dirs(known))
        self.bases = sorted(bases, key=lambda base: (-base.count("/") - bool(base), base))

    def resolve(self, importer: str, statement: PythonImport) -> list[ImportRecord]:
        """Return one record per resolved target file, or one unresolved record."""
        parts = statement.module.split(".") if statement.module else []
        for base in self._bases_for(importer, statement):
            records = self._from_base(base, parts, statement)
            if records:
                return records
        return [_record(statement, None, statement.names)]

    def _bases_for(self, importer: str, statement: PythonImport) -> list[str]:
        if statement.level == 0:
            return self.bases
        package = posixpath.dirname(importer)
        for _ in range(statement.level - 1):
            package = posixpath.dirname(package)
        return [package]

    def _from_base(self, base: str, parts: list[str], statement: PythonImport) -> list[ImportRecord]:
        records = []
        leftover = []
        for name in statement.names:
            submodule = self._module(base, parts + [name]) if name != "*" else None
            if submodule:
                records.append(_record(statement, submodule, ()))
            else:
                leftover.append(name)
        module = self._module(base, parts)
        if module and (leftover or not statement.names):
            records.append(_record(statement, module, tuple(leftover)))
        return records

    def _module(self, base: str, parts: list[str]) -> str | None:
        joined = posixpath.join(base, *parts) if parts else base
        for candidate in (joined + ".py", posixpath.join(joined, "__init__.py")):
            if parts and candidate in self.known:
                return candidate
        init = posixpath.join(joined, "__init__.py")
        return init if not parts and init in self.known else None


def _record(statement: PythonImport, target: str | None, names: tuple[str, ...]) -> ImportRecord:
    specifier = "." * statement.level + statement.module
    climb = max(statement.level - 1, 0)
    return ImportRecord(statement.line, specifier, climb, statement.type_only, names, target)


def _src_dirs(known: set[str]) -> set[str]:
    found = set()
    for path in known:
        parts = path.split("/")[:-1]
        for index, part in enumerate(parts):
            if part == "src":
                found.add("/".join(parts[: index + 1]))
    return found
