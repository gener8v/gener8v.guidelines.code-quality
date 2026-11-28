"""Map file names to languages and language families."""

from __future__ import annotations

import posixpath

EXTENSIONS = {
    ".py": "python",
    ".ts": "typescript",
    ".mts": "typescript",
    ".cts": "typescript",
    ".tsx": "tsx",
    ".js": "javascript",
    ".mjs": "javascript",
    ".cjs": "javascript",
    ".jsx": "jsx",
    ".go": "go",
    ".rs": "rust",
    ".rb": "ruby",
    ".java": "java",
    ".kt": "kotlin",
    ".cs": "csharp",
    ".swift": "swift",
    ".sh": "shell",
    ".bash": "shell",
    ".zsh": "shell",
}
SCRIPT_LANGUAGES = frozenset({"typescript", "tsx", "javascript", "jsx"})
C_LIKE_LANGUAGES = SCRIPT_LANGUAGES | {"go", "rust", "java", "kotlin", "csharp", "swift"}
CODE_LANGUAGES = frozenset(EXTENSIONS.values()) - {"shell"}
SCRIPT_EXTENSIONS = (".ts", ".tsx", ".mts", ".cts", ".js", ".jsx", ".mjs", ".cjs")
DECLARATION_SUFFIXES = (".d.ts", ".d.mts", ".d.cts")


def language_of(path: str) -> str | None:
    """Return the language of a file from its extension, or None."""
    return EXTENSIONS.get(posixpath.splitext(path)[1].lower())


def family_of(language: str | None) -> str | None:
    """Group TypeScript and JavaScript as `script`, Java and Kotlin as `jvm`."""
    if language in SCRIPT_LANGUAGES:
        return "script"
    if language in ("java", "kotlin"):
        return "jvm"
    return language


def is_declaration(path: str) -> bool:
    """Return True for TypeScript declaration files such as `env.d.ts`."""
    return path.endswith(DECLARATION_SUFFIXES)


def stem_of(path: str) -> str:
    """Return the file name without its extension (and without `.d` for declarations)."""
    name = posixpath.basename(path)
    for suffix in DECLARATION_SUFFIXES:
        if name.endswith(suffix):
            return name[: -len(suffix)]
    return posixpath.splitext(name)[0]
