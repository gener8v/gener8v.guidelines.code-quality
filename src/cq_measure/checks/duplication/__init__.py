"""Checks for section 7: duplication and dead code."""

from cq_measure.checks.duplication.commented_code import check_commented_code
from cq_measure.checks.duplication.duplicate_blocks import check_duplicate_block
from cq_measure.checks.duplication.orphans import check_orphan_file
from cq_measure.checks.duplication.unused_symbols import check_unused_symbol

CHECKS = {
    "duplicate-block": check_duplicate_block,
    "orphan-file": check_orphan_file,
    "unused-symbol": check_unused_symbol,
    "commented-code": check_commented_code,
}
