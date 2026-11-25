"""Resolve TypeScript and JavaScript import specifiers to repository files."""

from __future__ import annotations

import posixpath

from cq_measure.imports.tsconfig import AliasConfig

EXTENSIONS = (".ts", ".tsx", ".d.ts", ".js", ".jsx", ".mjs", ".cjs", ".mts", ".cts")
_JS_TO_TS = {".js": (".ts", ".tsx"), ".jsx": (".tsx",), ".mjs": (".mts",), ".cjs": (".cts",)}


class ScriptResolver:
    """Maps a specifier to a file: relative paths, tsconfig aliases, `.js` to `.ts`, `index` files."""

    def __init__(self, known: set[str], aliases: dict[str, AliasConfig]):
        self.known = known
        self.aliases = aliases

    def resolve(self, importer: str, specifier: str) -> str | None:
        """Return the repository file that `specifier` names, or None for a package or a miss."""
        if specifier.startswith("."):
            base = posixpath.normpath(posixpath.join(posixpath.dirname(importer), specifier))
            return self.find_file(base)
        config = self._config_for(posixpath.dirname(importer))
        if config is None:
            return None
        for base in config.candidates(specifier):
            found = self.find_file(base)
            if found:
                return found
        return None

    def _config_for(self, directory: str) -> AliasConfig | None:
        current = directory
        while True:
            if current in self.aliases:
                return self.aliases[current]
            if not current:
                return None
            current = posixpath.dirname(current)

    def find_file(self, base: str) -> str | None:
        """Return the first existing file for a path without (or with) an extension."""
        if base == ".." or base.startswith("../"):
            return None
        for candidate in _candidates(base):
            if candidate in self.known:
                return candidate
        return None


def _candidates(base: str) -> list[str]:
    stem, extension = posixpath.splitext(base)
    found = [base]
    found.extend(stem + replacement for replacement in _JS_TO_TS.get(extension, ()))
    found.extend(base + extension_ for extension_ in EXTENSIONS)
    found.extend(posixpath.join(base, "index" + extension_) for extension_ in EXTENSIONS)
    return found
