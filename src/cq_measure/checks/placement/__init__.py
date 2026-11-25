"""Checks for section 6: test placement."""

from cq_measure.checks.placement.colocation import check_test_colocation, check_test_name
from cq_measure.checks.placement.untested import check_untested_file

CHECKS = {
    "test-colocation": check_test_colocation,
    "test-name": check_test_name,
    "untested-file": check_untested_file,
}
