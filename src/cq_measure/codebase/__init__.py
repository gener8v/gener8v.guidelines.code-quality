"""Find the files of a repository and read their source text."""

from cq_measure.codebase.directory_tree import build_directories, has_hidden_part
from cq_measure.codebase.discovery import discover
from cq_measure.codebase.file_roles import (
    GENERATED_DIRS,
    ROUTE_DIRS,
    generated_marker_line,
    in_route_tree,
    in_script_dir,
    is_cli_entry,
    is_config_name,
    is_entry_point,
    is_framework_file,
    is_generated,
    is_test_file,
    is_testish,
    test_subject,
)
from cq_measure.codebase.globs import matches_any
from cq_measure.codebase.language import (
    CODE_LANGUAGES,
    SCRIPT_LANGUAGES,
    family_of,
    is_declaration,
    language_of,
    stem_of,
)
from cq_measure.codebase.package_roots import (
    is_within,
    nearest_root,
    package_roots,
    parts_of,
)
from cq_measure.codebase.scanning.comments import comments_of, python_comments
from cq_measure.codebase.scanning.lexer import scan_source
from cq_measure.codebase.scanning.scan import Scan
from cq_measure.codebase.source_file import SourceFile
from cq_measure.codebase.typescript_compiler import (
    CompilerResult,
    measure_with_compiler,
)

__all__ = [
    "CODE_LANGUAGES",
    "CompilerResult",
    "GENERATED_DIRS",
    "ROUTE_DIRS",
    "SCRIPT_LANGUAGES",
    "Scan",
    "SourceFile",
    "build_directories",
    "comments_of",
    "discover",
    "family_of",
    "generated_marker_line",
    "has_hidden_part",
    "in_route_tree",
    "in_script_dir",
    "is_cli_entry",
    "is_config_name",
    "is_declaration",
    "is_entry_point",
    "is_framework_file",
    "is_generated",
    "is_test_file",
    "is_testish",
    "is_within",
    "language_of",
    "matches_any",
    "measure_with_compiler",
    "nearest_root",
    "package_roots",
    "parts_of",
    "python_comments",
    "scan_source",
    "stem_of",
    "test_subject",
]
