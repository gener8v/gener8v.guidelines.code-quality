"""Collect the findings of one check and grade measured values."""

from __future__ import annotations

from cq_measure.reporting.findings import Finding

Location = tuple  # (path, line or None)


class Emitter:
    """Builds findings for one check from its configuration entry."""

    def __init__(self, check_id: str, spec: dict):
        self.check = check_id
        self.spec = spec
        self.findings: list[Finding] = []

    def option(self, key: str, default=None):
        """Return an extra setting of this check, such as `min_lines`."""
        return self.spec.get(key, default)

    def flag(self, at: Location, message: str, *, test: bool = False) -> None:
        """Report a finding at the check's fixed severity, or at `test_severity` in a test file."""
        severity = self.spec.get("severity", "warn")
        if test:
            severity = self.spec.get("test_severity", severity)
        self._add(at, severity, message)

    def measure(self, at: Location, value: int, text: tuple[str, str], *, test: bool = False) -> None:
        """Report `value` when it is above the warn or fail threshold.

        `text` is (description of the measured value, advice). The message
        reads: "<description>; <severity> above <limit>. <advice>".
        """
        warn, fail = self._limits(test=test)
        if fail is not None and value > fail:
            severity, limit = "fail", fail
        elif warn is not None and value > warn:
            severity, limit = "warn", warn
        else:
            return
        describe, advice = text
        self._add(at, severity, f"{describe}; {severity} above {limit}. {advice}")

    def _limits(self, *, test: bool) -> tuple:
        if test and "test_warn" in self.spec:
            return self.spec.get("test_warn"), self.spec.get("test_fail")
        return self.spec.get("warn"), self.spec.get("fail")

    def _add(self, at: Location, severity: str, message: str) -> None:
        path, line = at
        self.findings.append(Finding(path, line, self.spec.get("rule"), self.check, severity, message))
