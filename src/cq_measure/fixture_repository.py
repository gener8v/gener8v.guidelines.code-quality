"""Build small repositories in temporary directories for the unit tests."""

from __future__ import annotations

import tempfile
from contextlib import contextmanager
from pathlib import Path

from cq_measure.config import deep_merge, load_defaults
from cq_measure.runner import measure


@contextmanager
def fixture_repo(files: dict[str, str]):
    """Write `files` (relative path -> text) into a temporary directory and yield its path."""
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        for relative, text in files.items():
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
        yield root


def findings_for(files: dict[str, str], check: str, config: dict | None = None) -> list:
    """Return the findings of one check on a repository made of `files`."""
    with fixture_repo(files) as root:
        merged = deep_merge(load_defaults(), config or {})
        return measure(root, merged, {check})
