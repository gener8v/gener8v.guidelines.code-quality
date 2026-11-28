"""List the files of a repository: tracked and untracked-but-not-ignored files."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

from cq_measure.codebase.globs import matches_any

MAX_BYTES = 1024 * 1024
SKIPPED_WALK_DIRS = frozenset({".git", ".hg", ".svn", ".tox", ".nox", ".mypy_cache", ".pytest_cache", ".ruff_cache"})


def discover(root: Path, ignore: list[str]) -> list[str]:
    """Return the readable text files under `root`, as sorted relative paths."""
    paths = git_files(root)
    if paths is None:
        paths = walk_files(root)
    kept = (path for path in paths if not matches_any(path, ignore))
    return sorted(path for path in kept if is_text_file(root / path))


def git_files(root: Path) -> list[str] | None:
    """Return `git ls-files` output for a work tree, or None when `root` is not in one."""
    try:
        probe = _git(root, "rev-parse", "--is-inside-work-tree")
    except OSError:
        return None
    if probe.returncode != 0 or probe.stdout.strip() != b"true":
        return None
    listing = _git(root, "ls-files", "-z", "--cached", "--others", "--exclude-standard")
    return [name for name in listing.stdout.decode("utf-8", "replace").split("\0") if name]


def _git(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, check=False)


def walk_files(root: Path) -> list[str]:
    """Return every file below `root`, skipping version-control and cache directories."""
    found = []
    for current, dirs, files in os.walk(root):
        dirs[:] = [name for name in dirs if name not in SKIPPED_WALK_DIRS and not name.endswith(".egg-info")]
        relative = Path(current).relative_to(root).as_posix()
        prefix = "" if relative == "." else relative + "/"
        found.extend(prefix + name for name in files)
    return found


def is_text_file(path: Path) -> bool:
    """Return True for a regular file of at most 1 MB with no NUL byte in its first 8 KB."""
    if path.is_symlink() or not path.is_file():
        return False
    if path.stat().st_size > MAX_BYTES:
        return False
    with path.open("rb") as handle:
        return b"\0" not in handle.read(8192)
