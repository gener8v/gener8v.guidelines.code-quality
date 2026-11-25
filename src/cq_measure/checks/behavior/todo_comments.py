"""Rule 14.4: every TODO names an issue."""

from __future__ import annotations

import re

_MARKER = re.compile(r"^[@\W]*(TODO|FIXME|HACK|XXX)\b(?=\s*[:(]|\s+\S|\s*$)")
_ISSUE = re.compile(r"#\d+|\b[A-Z][A-Z0-9]+-\d+\b|https?://")


def todo_lines(comments) -> list[tuple[int, str]]:
    """Return (line, marker) for TODO-style comments without an issue reference on that line or the next."""
    by_line = {comment.line: comment.text for comment in comments}
    found = []
    for comment in comments:
        match = _MARKER.match(comment.text)
        if not match:
            continue
        following = by_line.get(comment.line + 1, "")
        nearby = comment.text + ("" if _MARKER.match(following) else " " + following)
        if not _ISSUE.search(nearby):
            found.append((comment.line, match.group(1)))
    return found


def check_todo_without_issue(workspace, emit) -> None:
    for source in workspace.sources:
        if workspace.generated(source):
            continue
        for line, marker in todo_lines(workspace.comments(source)):
            emit.flag((source.path, line), f"`{marker}` without an issue reference. Add the issue (`#123`, `ABC-123`, or a URL), or delete it.")
