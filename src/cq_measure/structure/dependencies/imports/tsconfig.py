"""Read path aliases (`baseUrl` and `paths`) from tsconfig.json and jsconfig.json."""

from __future__ import annotations

import json
import posixpath
import re
from collections import defaultdict
from dataclasses import dataclass, field

_CONFIG_NAME = re.compile(r"^(tsconfig(\..+)?|jsconfig)\.json$")
_TRAILING_COMMA = re.compile(r",(\s*[}\]])")
_JSON_TOKENS = re.compile(r'"(?:\\.|[^"\\])*"|//[^\n]*|/\*[\s\S]*?\*/')


def strip_json_comments(text: str) -> str:
    """Remove `//` and `/* */` comments and trailing commas, keeping string contents."""

    def keep_strings(match: re.Match) -> str:
        token = match.group()
        return token if token.startswith('"') else ""

    return _TRAILING_COMMA.sub(r"\1", _JSON_TOKENS.sub(keep_strings, text))


@dataclass
class AliasConfig:
    """Path aliases of one directory. Targets are repository-relative paths with `*`."""

    base_url: str | None = None
    paths: dict[str, list[str]] = field(default_factory=dict)

    def candidates(self, specifier: str) -> list[str]:
        """Return the repository paths (without extension) that a bare specifier may mean."""
        found = []
        for pattern, targets in self.paths.items():
            star = _match_pattern(pattern, specifier)
            if star is not None:
                found.extend(target.replace("*", star) for target in targets)
        if self.base_url is not None:
            found.append(posixpath.normpath(posixpath.join(self.base_url, specifier)))
        return found


def _match_pattern(pattern: str, specifier: str) -> str | None:
    if "*" not in pattern:
        return "" if pattern == specifier else None
    prefix, suffix = pattern.split("*", 1)
    if len(specifier) < len(prefix) + len(suffix):
        return None
    if specifier.startswith(prefix) and specifier.endswith(suffix):
        return specifier[len(prefix) : len(specifier) - len(suffix)]
    return None


def load_alias_configs(read, paths) -> dict[str, AliasConfig]:
    """Return the alias configuration of each directory that holds a tsconfig or jsconfig file.

    `read(path)` returns the text of a repository file, or None.
    """
    by_directory = defaultdict(list)
    for path in paths:
        if _CONFIG_NAME.match(posixpath.basename(path)):
            by_directory[posixpath.dirname(path)].append(path)
    configs = {}
    for directory, files in by_directory.items():
        config = AliasConfig()
        for path in sorted(files, key=lambda name: (posixpath.basename(name) != "tsconfig.json", name)):
            _merge(config, _read_options(read, path, 0))
        if config.paths or config.base_url is not None:
            configs[directory] = config
    return configs


def _merge(config: AliasConfig, options: AliasConfig) -> None:
    if config.base_url is None:
        config.base_url = options.base_url
    for pattern, targets in options.paths.items():
        config.paths.setdefault(pattern, targets)


def _read_options(read, path: str, depth: int) -> AliasConfig:
    data = _parse(read(path))
    here = posixpath.dirname(path)
    result = _own_options(data.get("compilerOptions") or {}, here)
    parent = data.get("extends")
    if isinstance(parent, str) and parent.startswith(".") and depth < 5:
        parent_path = posixpath.normpath(posixpath.join(here, parent))
        parent_path += "" if parent_path.endswith(".json") else ".json"
        _merge(result, _read_options(read, parent_path, depth + 1))
    return result


def _own_options(options: dict, here: str) -> AliasConfig:
    """Return `baseUrl` and `paths` of one file, made relative to the repository root."""
    result = AliasConfig()
    if isinstance(options.get("baseUrl"), str):
        result.base_url = posixpath.normpath(posixpath.join(here, options["baseUrl"]))
    anchor = result.base_url if result.base_url is not None else here
    paths = options.get("paths")
    for pattern, targets in (paths.items() if isinstance(paths, dict) else ()):
        if isinstance(targets, list):
            result.paths[pattern] = [posixpath.normpath(posixpath.join(anchor, t)) for t in targets if isinstance(t, str)]
    return result


def _parse(text: str | None) -> dict:
    if not text:
        return {}
    try:
        data = json.loads(strip_json_comments(text))
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}
