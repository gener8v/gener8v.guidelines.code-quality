"""Checks for section 3: packages and the dependencies between them."""

from cq_measure.checks.packages.boundaries import check_deep_import, check_layer_direction, check_relative_climb
from cq_measure.checks.packages.cycles import check_file_cycle, check_import_cycle
from cq_measure.checks.packages.fan_out import check_fan_out

CHECKS = {
    "deep-import": check_deep_import,
    "relative-climb": check_relative_climb,
    "layer-direction": check_layer_direction,
    "import-cycle": check_import_cycle,
    "file-cycle": check_file_cycle,
    "fan-out": check_fan_out,
}
