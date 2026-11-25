"""Pick the Python or the TypeScript measures for one file."""

from __future__ import annotations

from cq_measure.metrics.python_classes import python_classes
from cq_measure.metrics.python_metrics import measure_python
from cq_measure.metrics.script_classes import script_classes
from cq_measure.metrics.script_functions import find_functions, match_brackets
from cq_measure.metrics.script_metrics import measure_script
from cq_measure.source.language import SCRIPT_LANGUAGES, is_declaration


def functions_of(source, tree, scan_of) -> list:
    """Return the function measures of a file. `scan_of(source)` lexes TypeScript and JavaScript."""
    if source.language == "python":
        return measure_python(tree, source.lines) if tree else []
    if source.language in SCRIPT_LANGUAGES and not is_declaration(source.path):
        return measure_script(scan_of(source), source.lines)
    return []


def classes_of(source, tree, scan_of) -> list:
    """Return the classes of a file, and the interfaces of a TypeScript file."""
    if source.language == "python":
        return python_classes(tree) if tree else []
    if source.language in SCRIPT_LANGUAGES:
        scan = scan_of(source)
        pairs = match_brackets(scan.code)
        return script_classes(scan, find_functions(scan, pairs), pairs)
    return []
