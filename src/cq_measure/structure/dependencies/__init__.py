"""Checks for section 3: packages and the dependencies between them."""

from cq_measure.structure.dependencies.cycles import (
    check_file_cycle,
    check_import_cycle,
)
from cq_measure.structure.dependencies.deep_import import check_deep_import
from cq_measure.structure.dependencies.fan_out import check_fan_out
from cq_measure.structure.dependencies.graph import ModuleGraph, build_graph
from cq_measure.structure.dependencies.imports.script_exports import script_exports
from cq_measure.structure.dependencies.layer_direction import check_layer_direction
from cq_measure.structure.dependencies.relative_climb import check_relative_climb

CHECKS = {
    "deep-import": check_deep_import,
    "relative-climb": check_relative_climb,
    "layer-direction": check_layer_direction,
    "import-cycle": check_import_cycle,
    "file-cycle": check_file_cycle,
    "fan-out": check_fan_out,
}

__all__ = [
    "CHECKS",
    "ModuleGraph",
    "build_graph",
    "script_exports",
]
