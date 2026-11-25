"""Finding records and the order of severities."""

from __future__ import annotations

from dataclasses import asdict, dataclass

SEVERITY_RANKS = {"warn": 1, "fail": 2, "never": 3}


def severity_rank(severity: str) -> int:
    """Return a number that orders severities: warn < fail < never."""
    return SEVERITY_RANKS.get(severity, 0)


@dataclass(frozen=True)
class Finding:
    """One rule violation at a path and an optional line."""

    path: str
    line: int | None
    rule: str | None
    check: str
    severity: str
    message: str

    def to_dict(self) -> dict:
        return asdict(self)


def sort_key(finding: Finding) -> tuple:
    """Order findings by path, then line, then check id."""
    return (finding.path, finding.line or 0, finding.check, finding.message)
