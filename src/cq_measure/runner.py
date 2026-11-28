"""Run the enabled checks over a workspace and filter what they find."""

from __future__ import annotations

import subprocess
from pathlib import Path

from cq_measure.checks import CHECKS
from cq_measure.codebase import is_within
from cq_measure.reporting import Emitter, Finding, apply_suppressions, sort_key
from cq_measure.workspace import Workspace, load_workspace


class UsageError(Exception):
    """The command line asks for something that cannot be done."""


def run_checks(workspace: Workspace, only: set[str] | None = None) -> list[Finding]:
    """Run each enabled check (or only the named ones), then apply inline suppressions."""
    findings: list[Finding] = []
    for check_id, check in CHECKS.items():
        spec = workspace.config["checks"].get(check_id, {})
        if not spec.get("enabled", True) or (only and check_id not in only):
            continue
        emitter = Emitter(check_id, spec)
        check(workspace, emitter)
        findings.extend(emitter.findings)
    return sorted(apply_suppressions(workspace, findings), key=sort_key)


def measure(root: Path, config: dict, only: set[str] | None = None) -> list[Finding]:
    """Discover the files under `root` and return the findings of the checks."""
    return run_checks(load_workspace(root, config), only)


def keep_paths(findings: list[Finding], paths: list[str]) -> list[Finding]:
    """Keep the findings in the given files or directories (relative to the root)."""
    wanted = [path.strip("/") if path not in (".", "./") else "" for path in paths]
    return [finding for finding in findings if any(is_within(finding.path, path) for path in wanted)]


def changed_files(root: Path, ref: str) -> list[str]:
    """Return the files changed since `ref`, plus untracked files, relative to `root`."""
    diff = _git(root, "diff", "--name-only", "--relative", ref, "--")
    untracked = _git(root, "ls-files", "--others", "--exclude-standard")
    return sorted(set(diff.splitlines()) | set(untracked.splitlines()))


def _git(root: Path, *args: str) -> str:
    try:
        result = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, check=False)
    except OSError as error:
        raise UsageError(f"cannot run git: {error}") from error
    if result.returncode != 0:
        raise UsageError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout
