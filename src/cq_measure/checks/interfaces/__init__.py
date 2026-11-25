"""Checks for section 5: interfaces and abstraction."""

from cq_measure.checks.interfaces.inheritance import check_inheritance_depth, check_pass_through
from cq_measure.checks.interfaces.interface_checks import (
    check_impl_naming,
    check_interface_size,
    check_single_implementation,
)

CHECKS = {
    "single-implementation": check_single_implementation,
    "interface-size": check_interface_size,
    "pass-through": check_pass_through,
    "inheritance-depth": check_inheritance_depth,
    "impl-naming": check_impl_naming,
}
