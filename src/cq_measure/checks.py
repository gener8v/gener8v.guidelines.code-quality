"""All checks, keyed by check id, in the order of the guidelines."""

from cq_measure.behavior import CHECKS as BEHAVIOR_CHECKS
from cq_measure.reporting import check_suppression_reason
from cq_measure.structure import CHECKS as STRUCTURE_CHECKS

CHECKS = {
    **STRUCTURE_CHECKS,
    **BEHAVIOR_CHECKS,
    "suppression-reason": check_suppression_reason,
}
