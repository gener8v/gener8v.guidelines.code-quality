"""Checks for section 5: interfaces and abstraction."""

from cq_measure.structure.abstraction.impl_naming import check_impl_naming
from cq_measure.structure.abstraction.inheritance_depth import check_inheritance_depth
from cq_measure.structure.abstraction.interface_size import check_interface_size
from cq_measure.structure.abstraction.pass_through import check_pass_through
from cq_measure.structure.abstraction.single_implementation import (
    check_single_implementation,
)

CHECKS = {
    "single-implementation": check_single_implementation,
    "interface-size": check_interface_size,
    "pass-through": check_pass_through,
    "inheritance-depth": check_inheritance_depth,
    "impl-naming": check_impl_naming,
}
