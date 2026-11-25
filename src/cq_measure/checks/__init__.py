"""All checks, keyed by check id, in the order of the guidelines."""

from cq_measure.checks.behavior import CHECKS as BEHAVIOR_CHECKS
from cq_measure.checks.directories import CHECKS as DIRECTORY_CHECKS
from cq_measure.checks.duplication import CHECKS as DUPLICATION_CHECKS
from cq_measure.checks.files import CHECKS as FILE_CHECKS
from cq_measure.checks.functions import CHECKS as FUNCTION_CHECKS
from cq_measure.checks.interfaces import CHECKS as INTERFACE_CHECKS
from cq_measure.checks.packages import CHECKS as PACKAGE_CHECKS
from cq_measure.checks.placement import CHECKS as PLACEMENT_CHECKS
from cq_measure.suppression import check_suppression_reason

CHECKS = {
    **FILE_CHECKS,
    **DIRECTORY_CHECKS,
    **PACKAGE_CHECKS,
    **FUNCTION_CHECKS,
    **INTERFACE_CHECKS,
    **PLACEMENT_CHECKS,
    **DUPLICATION_CHECKS,
    **BEHAVIOR_CHECKS,
    "suppression-reason": check_suppression_reason,
}
