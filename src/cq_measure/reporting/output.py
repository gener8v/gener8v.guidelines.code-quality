"""Format findings as text or JSON, with a summary."""

from __future__ import annotations

import json
from collections import Counter, defaultdict

from cq_measure.reporting.findings import Finding


def summarize(findings: list[Finding], file_count: int, typescript: dict | None = None) -> dict:
    """Count findings per severity and per check. `typescript` says how TypeScript and JavaScript files were measured."""
    by_check: dict[str, Counter] = defaultdict(Counter)
    for finding in findings:
        by_check[finding.check][finding.severity] += 1
    severities = Counter(finding.severity for finding in findings)
    return {
        "files": file_count,
        "total": len(findings),
        "fail": severities.get("fail", 0),
        "warn": severities.get("warn", 0),
        "by_check": {check: dict(sorted(counts.items())) for check, counts in sorted(by_check.items())},
        "typescript": typescript,
    }


def render_json(findings: list[Finding], summary: dict) -> str:
    return json.dumps({"findings": [finding.to_dict() for finding in findings], "summary": summary}, indent=2)


def render_text(findings: list[Finding], summary: dict) -> str:
    """One line per finding (`path:line  rule  check  severity  message`), then the summary."""
    lines = [_finding_line(finding) for finding in findings]
    if lines:
        lines.append("")
    lines.append(f"{summary['files']} files measured: {summary['fail']} fail, {summary['warn']} warn.")
    width = max((len(check) for check in summary["by_check"]), default=0)
    for check, counts in summary["by_check"].items():
        parts = ", ".join(f"{count} {severity}" for severity, count in counts.items())
        lines.append(f"  {check.ljust(width)}  {parts}")
    if summary.get("typescript"):
        lines.append(typescript_note(summary["typescript"]))
    return "\n".join(lines) + "\n"


def typescript_note(status: dict) -> str:
    """Say whether the TypeScript and JavaScript functions were measured exactly."""
    if status["measured_by"] == "compiler":
        return f"TypeScript and JavaScript functions were measured with the TypeScript compiler {status['version']}."
    return (
        f"TypeScript and JavaScript functions were measured approximately ({status['reason']}). "
        "For exact measures, install Node.js and typescript 5 or 6, in the repository or with CQ_TYPESCRIPT set to its path."
    )


def _finding_line(finding: Finding) -> str:
    where = finding.path if finding.line is None else f"{finding.path}:{finding.line}"
    rule = finding.rule or "-"
    return f"{where}  {rule}  {finding.check}  {finding.severity}  {finding.message}"
