"""Rule 7.2: delete files that nothing uses."""

from __future__ import annotations

import posixpath
import re
from functools import lru_cache

from cq_measure.source.language import SCRIPT_LANGUAGES, is_declaration
from cq_measure.source.roles import is_entry_point, is_testish

GRAPH_LANGUAGES = SCRIPT_LANGUAGES | {"python"}


def reference_tokens(path: str) -> list[str]:
    """Return the ways another file may name this file: its file name, short path, or dotted module."""
    stem_path = posixpath.splitext(path)[0]
    parts = stem_path.split("/")
    tokens = [posixpath.basename(path)]
    if len(parts) >= 2:
        tokens.append("/".join(parts[-2:]))
        if path.endswith(".py"):
            tokens.append(".".join(parts[-2:]))
    return tokens


class _Corpus:
    """All file texts joined, to count how often a token occurs outside one file."""

    def __init__(self, workspace):
        self.text = "\0".join(source.text for source in workspace.files)

    def mentioned_outside(self, token: str, own_text: str) -> bool:
        pattern = _token_pattern(token)
        return len(pattern.findall(self.text)) > len(pattern.findall(own_text))


@lru_cache(maxsize=4096)
def _token_pattern(token: str) -> re.Pattern:
    return re.compile(r"(?<![\w.-])" + re.escape(token) + r"(?![\w-])")


def _candidate(workspace, source) -> bool:
    if source.language not in GRAPH_LANGUAGES or is_testish(source.path) or is_declaration(source.path):
        return False
    if workspace.graph.importers.get(source.path) or workspace.generated(source):
        return False
    return not is_entry_point(source, workspace.config["entry_points"])


def check_orphan_file(workspace, emit) -> None:
    corpus = None
    for source in workspace.sources:
        if not _candidate(workspace, source):
            continue
        corpus = corpus or _Corpus(workspace)
        if any(corpus.mentioned_outside(token, source.text) for token in reference_tokens(source.path)):
            continue
        emit.flag((source.path, None), "No file imports or names this file, and it is not an entry point. Delete it, or add it to `entry_points`.")
