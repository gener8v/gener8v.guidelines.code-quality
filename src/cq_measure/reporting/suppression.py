"""Inline suppression: a comment `cq-ignore <check-id>: <reason>`.

On a line, the comment suppresses that check on that line. On one of the
first five lines of a file, it suppresses that check for the whole file.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from cq_measure.reporting.findings import Finding

MARKER = "cq-ignore"
HEADER_LINES = 5
_SUPPRESSION = re.compile(r"cq-ignore\s+([a-z0-9-]+(?:\s*,\s*[a-z0-9-]+)*)\s*(?::\s*(\S.*))?")


@dataclass
class FileSuppressions:
    """The checks suppressed in one file: for the whole file, and per line."""

    whole_file: set[str] = field(default_factory=set)
    by_line: dict[int, set[str]] = field(default_factory=dict)
    unexplained: list[tuple[int, str]] = field(default_factory=list)

    def covers(self, finding: Finding) -> bool:
        if finding.check in self.whole_file:
            return True
        return finding.line is not None and finding.check in self.by_line.get(finding.line, set())


def parse_suppressions(comments) -> FileSuppressions:
    """Read the suppression comments of one file."""
    result = FileSuppressions()
    for comment in comments:
        match = _SUPPRESSION.search(comment.text)
        if not match:
            continue
        ids = {part.strip() for part in match.group(1).split(",")}
        if comment.line <= HEADER_LINES:
            result.whole_file |= ids
        result.by_line.setdefault(comment.line, set()).update(ids)
        if not match.group(2):
            result.unexplained.append((comment.line, ", ".join(sorted(ids))))
    return result


def suppressions_of(workspace, source) -> FileSuppressions:
    """Return the suppressions of a file, reading comments only when the marker is present."""
    if MARKER not in source.text:
        return FileSuppressions()
    return workspace.cached("suppressions", source, lambda s: parse_suppressions(workspace.comments(s)))


def apply_suppressions(workspace, findings: list[Finding]) -> list[Finding]:
    """Drop the findings that an inline suppression covers."""
    kept = []
    for finding in findings:
        source = workspace.by_path.get(finding.path)
        if source is None or not suppressions_of(workspace, source).covers(finding):
            kept.append(finding)
    return kept


def check_suppression_reason(workspace, emit) -> None:
    """Report suppressions that give no reason after a colon."""
    for source in workspace.sources:
        for line, ids in suppressions_of(workspace, source).unexplained:
            emit.flag((source.path, line), f"Suppression of `{ids}` gives no reason. Write `cq-ignore {ids}: <why>`.")
