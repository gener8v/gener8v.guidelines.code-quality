"""Rule 16.1: no secrets in the repository. Output shows only the first four characters."""

from __future__ import annotations

import re

from cq_measure.source.roles import is_testish

TOKEN_PATTERNS = (
    ("AWS access key id", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("private key", re.compile(r"-----BEGIN (?:[A-Z0-9]+ )*PRIVATE KEY(?: BLOCK)?-----")),
    ("GitHub token", re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{22,})")),
    ("Slack token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}")),
    ("API key", re.compile(r"\bsk-(?:[A-Za-z0-9]+-)*[A-Za-z0-9_]{20,}")),
)
_ASSIGNMENT = re.compile(
    r"""(?i)\b([\w-]*(?:password|passwd|secret|token|api[_-]?key)[\w-]*)["']?\s*(?::=|=|:)\s*(["'])([^"'\s]{8,})\2"""
)
_NOT_SECRET_NAME = re.compile(
    r"(?i)(url|uri|endpoint|path|field|name|type|label|_id$|-id$|header|param|length|min|max|pattern|regex|hint|"
    r"prompt|placeholder|env|file|prefix|suffix|count|expir|ttl|limit|kind|arn|tokeniz|tokens|policy|key_id|keyid)"
)
_PLACEHOLDER = re.compile(r"(?i)(example|sample|dummy|placeholder|changeme|your|xxxx|\*\*\*|\.\.\.|redacted|fake|test)")
_NOT_A_VALUE = re.compile(r"^(?:[a-z_.\-]+|[A-Z_.\-]+|[$<{%].*|https?:.*|\.?/.*)$")
ASSIGNMENT_SUFFIXES = (".py", ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".go", ".rb", ".java", ".kt", ".cs",
                       ".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".env", ".properties", ".tf", ".sh")
LOCK_FILES = re.compile(r"(?:^|/)(?:package-lock\.json|yarn\.lock|pnpm-lock\.yaml|poetry\.lock|uv\.lock|Cargo\.lock|go\.sum)$")


def mask(value: str) -> str:
    """Show the first four characters only."""
    return value[:4] + "****"


def token_findings(text: str) -> list[tuple[int, str]]:
    """Return (line, message) for well-known token formats."""
    found = []
    for label, pattern in TOKEN_PATTERNS:
        for match in pattern.finditer(text):
            value = match.group()
            if looks_fake(value) or (label == "API key" and not _mixed(value.rsplit("-", 1)[-1])):
                continue
            found.append((text.count("\n", 0, match.start()) + 1, f"Possible {label} `{mask(value)}`."))
    return found


def looks_fake(value: str) -> bool:
    """Return True for placeholders and test values: `EXAMPLE`, `xxxx`, or runs like `abcde` or `12345`."""
    if _PLACEHOLDER.search(value):
        return True
    lowered = value.lower()
    run = 1
    for previous, current in zip(lowered, lowered[1:]):
        run = run + 1 if ord(current) - ord(previous) in (0, 1) and current.isalnum() else 1
        if run >= 5:
            return True
    return False


def _mixed(value: str) -> bool:
    has_digit = any(char.isdigit() for char in value)
    return has_digit and any(char.isalpha() for char in value)


def assignment_findings(text: str) -> list[tuple[int, str]]:
    """Return (line, message) for `password = "..."` style literals that look like real values."""
    found = []
    for match in _ASSIGNMENT.finditer(text):
        name, value = match.group(1), match.group(3)
        if looks_secret(name, value):
            found.append((text.count("\n", 0, match.start()) + 1, f"`{name}` is set to the literal `{mask(value)}`."))
    return found


def looks_secret(name: str, value: str) -> bool:
    """Return True for a secret-like name with a value that is not a placeholder, a word, or a path."""
    if _NOT_SECRET_NAME.search(name) or looks_fake(value) or _NOT_A_VALUE.match(value):
        return False
    mixed_case = any(c.isupper() for c in value) and any(c.islower() for c in value)
    return (_mixed(value) or mixed_case) and len(set(value)) >= 4


def check_secret_literal(workspace, emit) -> None:
    advice = "Load it from the environment or a secret store, and rotate it if it is real."
    for source in workspace.files:
        if LOCK_FILES.search(source.path):
            continue
        found = token_findings(source.text)
        if source.path.endswith(ASSIGNMENT_SUFFIXES) and not is_testish(source.path):
            found += assignment_findings(source.text)
        for line, message in found:
            emit.flag((source.path, line), f"{message} {advice}")
