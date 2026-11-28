"""Pick the Python or the TypeScript class descriptions for one file."""

from __future__ import annotations

from cq_measure.codebase import SCRIPT_LANGUAGES, CompilerResult
from cq_measure.structure.classes.class_info import ClassInfo
from cq_measure.structure.classes.python_classes import python_classes
from cq_measure.structure.classes.script_classes import script_classes
from cq_measure.structure.functions import find_functions, match_brackets


def classes_of(source, tree, scan_of, compiled: CompilerResult | None = None) -> list[ClassInfo]:
    """Return the classes of a file, and the interfaces of a TypeScript file."""
    if source.language == "python":
        return python_classes(tree) if tree else []
    if source.language not in SCRIPT_LANGUAGES:
        return []
    if compiled is not None and source.path in compiled.classes:
        return [_class_info(item) for item in compiled.classes[source.path]]
    scan = scan_of(source)
    pairs = match_brackets(scan.code)
    return script_classes(scan, find_functions(scan, pairs), pairs)


def _class_info(item: dict) -> ClassInfo:
    return ClassInfo(
        name=item["name"],
        line=item["line"],
        kind=item["kind"],
        bases=tuple(item["bases"]),
        implements=tuple(item["implements"]),
        methods=tuple(item["methods"]),
    )
