"""Pick the Python or the TypeScript function measures for one file."""

from __future__ import annotations

from cq_measure.codebase import JAVASCRIPT_LANGUAGES, CompilerResult, is_declaration
from cq_measure.structure.functions.approximation.javascript_metrics import (
    measure_javascript,
)
from cq_measure.structure.functions.function_measure import FunctionMeasure
from cq_measure.structure.functions.python_functions import measure_python


def functions_of(source, tree, scan_of, compiled: CompilerResult | None = None) -> list[FunctionMeasure]:
    """Return the function measures of a file.

    For TypeScript and JavaScript, use the compiler measures in `compiled` when
    they hold the file. Otherwise lex it with `scan_of(source)` and approximate.
    """
    if source.language == "python":
        return measure_python(tree, source.lines) if tree else []
    if source.language not in JAVASCRIPT_LANGUAGES or is_declaration(source.path):
        return []
    if compiled is not None and source.path in compiled.functions:
        return [FunctionMeasure(**item) for item in compiled.functions[source.path]]
    return measure_javascript(scan_of(source), source.lines)
