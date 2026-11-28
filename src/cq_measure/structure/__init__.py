"""Checks for Part A of the guidelines: structure (sections 1 to 7)."""

from cq_measure.structure.abstraction import CHECKS as ABSTRACTION_CHECKS
from cq_measure.structure.classes import CHECKS as CLASS_CHECKS
from cq_measure.structure.dependencies import CHECKS as DEPENDENCY_CHECKS
from cq_measure.structure.directories import CHECKS as DIRECTORY_CHECKS
from cq_measure.structure.duplication import CHECKS as DUPLICATION_CHECKS
from cq_measure.structure.files import CHECKS as FILE_CHECKS
from cq_measure.structure.functions import CHECKS as FUNCTION_CHECKS
from cq_measure.structure.test_placement import CHECKS as PLACEMENT_CHECKS

CHECKS = {
    **FILE_CHECKS,
    **DIRECTORY_CHECKS,
    **DEPENDENCY_CHECKS,
    **FUNCTION_CHECKS,
    **CLASS_CHECKS,
    **ABSTRACTION_CHECKS,
    **PLACEMENT_CHECKS,
    **DUPLICATION_CHECKS,
}
