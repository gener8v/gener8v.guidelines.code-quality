"""Load the default configuration and merge a repository's `.code-quality.json`."""

from __future__ import annotations

import json
from pathlib import Path

DEFAULTS_PATH = Path(__file__).with_name("defaults.json")
CONFIG_NAME = ".code-quality.json"


class ConfigError(Exception):
    """The repository configuration is not valid."""


def load_defaults() -> dict:
    """Return the built-in configuration."""
    return json.loads(DEFAULTS_PATH.read_text(encoding="utf-8"))


def load_config(root: Path) -> dict:
    """Return the defaults deep-merged with `<root>/.code-quality.json`, if it exists."""
    defaults = load_defaults()
    path = root / CONFIG_NAME
    if not path.is_file():
        return defaults
    try:
        override = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ConfigError(f"{CONFIG_NAME}: not valid JSON (line {error.lineno}: {error.msg}).") from error
    validate(override, defaults)
    return deep_merge(defaults, override)


def validate(override: object, defaults: dict) -> None:
    """Raise ConfigError when `override` has an unknown key or check id."""
    if not isinstance(override, dict):
        raise ConfigError(f"{CONFIG_NAME}: the top level must be a JSON object.")
    unknown = sorted(set(override) - set(defaults))
    if unknown:
        raise ConfigError(f"{CONFIG_NAME}: unknown key(s) {', '.join(unknown)}. Known keys: {', '.join(sorted(defaults))}.")
    checks = override.get("checks", {})
    if not isinstance(checks, dict):
        raise ConfigError(f"{CONFIG_NAME}: `checks` must be an object of check ids.")
    for check_id, spec in checks.items():
        if check_id not in defaults["checks"]:
            raise ConfigError(f"{CONFIG_NAME}: unknown check id `{check_id}`. Run `cq-measure --list-checks` for the ids.")
        if not isinstance(spec, dict):
            raise ConfigError(f"{CONFIG_NAME}: the entry for `{check_id}` must be an object.")


def deep_merge(base: dict, override: dict) -> dict:
    """Merge objects recursively. Lists and scalars in `override` replace those in `base`."""
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged
