"""The `cq-measure` command line."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from cq_measure.checks import CHECKS
from cq_measure.configuration import ConfigError, load_config
from cq_measure.reporting import render_json, render_text, severity_rank, summarize
from cq_measure.runner import UsageError, changed_files, keep_paths, run_checks
from cq_measure.workspace import load_workspace, typescript_status


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cq-measure", description="Measure a repository against the code-quality rules.")
    parser.add_argument("path", nargs="?", default=".", help="repository root to measure (default: .)")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--fail-on", choices=("fail", "warn", "never"), default="fail", help="exit 1 at or above this severity")
    parser.add_argument("--paths", nargs="+", metavar="P", help="report findings only in these files or directories")
    parser.add_argument("--changed-since", metavar="REF", help="report findings only in files changed since a git ref")
    parser.add_argument("--only", metavar="ID[,ID]", help="run only these checks")
    parser.add_argument("--list-checks", action="store_true", help="list the check ids and their thresholds")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return _run(args)
    except (ConfigError, UsageError) as error:
        sys.stderr.write(f"cq-measure: {error}\n")
        return 2


def _run(args: argparse.Namespace) -> int:
    root = Path(args.path).resolve()
    if not root.is_dir():
        raise UsageError(f"{args.path} is not a directory.")
    config = load_config(root)
    if args.list_checks:
        sys.stdout.write(list_checks(config))
        return 0
    workspace = load_workspace(root, config)
    findings = run_checks(workspace, _only(args.only, config))
    findings = _filter(findings, root, args)
    summary = summarize(findings, len(workspace.sources), typescript_status(workspace))
    render = render_json if args.format == "json" else render_text
    sys.stdout.write(render(findings, summary))
    threshold = severity_rank(args.fail_on)
    return 1 if any(severity_rank(finding.severity) >= threshold for finding in findings) else 0


def _only(value: str | None, config: dict) -> set[str] | None:
    if not value:
        return None
    ids = {part.strip() for part in value.split(",") if part.strip()}
    unknown = sorted(ids - set(config["checks"]))
    if unknown:
        raise UsageError(f"unknown check id(s): {', '.join(unknown)}. Run `cq-measure --list-checks`.")
    return ids


def _filter(findings: list, root: Path, args: argparse.Namespace) -> list:
    if args.paths:
        findings = keep_paths(findings, [_relative(root, path) for path in args.paths])
    if args.changed_since:
        findings = keep_paths(findings, changed_files(root, args.changed_since) or ["\0"])
    return findings


def _relative(root: Path, path: str) -> str:
    """Accept a path relative to the repository root, or one that exists relative to the current directory."""
    candidate = Path(path)
    if not candidate.is_absolute() and not candidate.exists():
        return candidate.as_posix()
    try:
        return candidate.resolve().relative_to(root).as_posix()
    except ValueError as error:
        raise UsageError(f"{path} is outside {root}.") from error


def list_checks(config: dict) -> str:
    """Return one line per check: id, rule, severity or thresholds, and whether it is enabled."""
    lines = []
    for check_id in CHECKS:
        spec = config["checks"].get(check_id, {})
        limits = spec.get("severity") or f"warn > {spec.get('warn')}, fail > {spec.get('fail')}"
        if "test_warn" in spec:
            limits += f" (tests: warn > {spec['test_warn']}, fail > {spec['test_fail']})"
        if "test_severity" in spec:
            limits += f" (tests: {spec['test_severity']})"
        state = "" if spec.get("enabled", True) else "  (disabled)"
        lines.append(f"{check_id:<22} {spec.get('rule') or '-':<5} {limits}{state}")
    return "\n".join(lines) + "\n"
