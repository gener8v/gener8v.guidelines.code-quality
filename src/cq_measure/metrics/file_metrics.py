"""Pick the Python or the TypeScript measures for one file."""

from __future__ import annotations

from cq_measure.metrics.python_classes import python_classes
from cq_measure.metrics.python_metrics import measure_python
from cq_measure.metrics.script_classes import script_classes
from cq_measure.metrics.script_functions import find_functions, match_brackets
from cq_measure.metrics.script_metrics import measure_script
from cq_measure.metrics.typescript_compiler import CompilerResult
from cq_measure.source.language import SCRIPT_LANGUAGES, is_declaration


def functions_of(source, tree, scan_of, compiled: CompilerResult | None = None) -> list:
    """Return the function measures of a file.

    For TypeScript and JavaScript, use the compiler measures in `compiled` when
    they hold the file. Otherwise lex it with `scan_of(source)` and approximate.
    """
    if source.language == "python":
        return measure_python(tree, source.lines) if tree else []
    if source.language not in SCRIPT_LANGUAGES or is_declaration(source.path):
        return []
    if compiled is not None and source.path in compiled.functions:
        return compiled.functions[source.path]
    return measure_script(scan_of(source), source.lines)


def classes_of(source, tree, scan_of, compiled: CompilerResult | None = None) -> list:
    """Return the classes of a file, and the interfaces of a TypeScript file."""
    if source.language == "python":
        return python_classes(tree) if tree else []
    if source.language in SCRIPT_LANGUAGES:
        if compiled is not None and source.path in compiled.classes:
            return compiled.classes[source.path]
        scan = scan_of(source)
        pairs = match_brackets(scan.code)
        return script_classes(scan, find_functions(scan, pairs), pairs)
    return []
