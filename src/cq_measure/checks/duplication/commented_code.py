"""Rule 7.4: do not leave commented-out code."""

from __future__ import annotations

import re

_CODE_LINE = re.compile(
    r"^(?:"
    r"(?:def|class)\s+\w+.*:$"
    r"|(?:import\s+[\w.]+(?:\s+as\s+\w+)?|from\s+[\w.]+\s+import\s+[\w*(].*)$"
    r"|(?:if|elif|while|for|with)\b[^.!?]*:$"
    r"|(?:if|while|for|switch)\s*\(.*\)\s*\{?$"
    r"|(?:else|try|finally)\s*[:{]?$|except\b.*:$|catch\s*\(.*\)\s*\{?$"
    r"|return(?:\s+[\w.\[\]()\"',]+)?;?$|(?:raise|throw)\s+\w+(?:\(.*\))?;?$"
    r"|(?:const|let|var)\s+[\w${}\[\], ]+\s*=.*$"
    r"|(?:export\s+)?(?:async\s+)?function\s*\*?\s*\w*\s*\(.*$"
    r"|[\w.$\[\]'\"]+\s*(?:[-+*/|&]?=)\s*[^=\s].*$"
    r"|[\w.$]+\(.*\)\s*;?$"
    r"|[}\])]+[;,)]*(?:\s*else\b.*)?$"
    r"|@\w[\w.]*(?:\(.*\))?$"
    r"|</?[A-Za-z][\w.]*(?:\s+[\w-]+=.*)?\s*/?>$"
    r")"
)
_DIRECTIVE = re.compile(r"^(?:type:|noqa|pragma|eslint|@ts-|prettier|istanbul|c8\b|cq-ignore|go:|nolint|region|endregion|-\*-|!)")
_PROSE = re.compile(r"^(?:[A-Za-z'’,]+\s+){5,}")


def looks_like_code(text: str) -> bool:
    """Return True when a comment line reads as a statement, not as prose."""
    stripped = text.strip()
    if not stripped or _DIRECTIVE.match(stripped) or _PROSE.match(stripped):
        return False
    return bool(_CODE_LINE.match(stripped))


def code_runs(comments, minimum: int) -> list[int]:
    """Return the first line of each run of `minimum` or more consecutive code-like comment lines."""
    starts = []
    run_start, run_length, previous = None, 0, None
    for comment in comments:
        contiguous = previous is not None and comment.line == previous + 1
        code = comment.own_line and comment.kind != "doc" and looks_like_code(comment.text)
        if code and contiguous and run_length:
            run_length += 1
        elif code:
            run_start, run_length = comment.line, 1
        else:
            run_length = 0
        if run_length == minimum:
            starts.append(run_start)
        previous = comment.line
    return starts


def check_commented_code(workspace, emit) -> None:
    minimum = emit.option("min_lines", 3)
    for source in workspace.sources:
        if workspace.generated(source):
            continue
        for line in code_runs(workspace.comments(source), minimum):
            emit.flag((source.path, line), f"{minimum} or more comment lines look like code. Delete commented-out code; git keeps the history.")
