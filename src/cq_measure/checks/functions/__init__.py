"""Checks for section 4: functions and classes."""

from cq_measure.checks.functions.flags_and_classes import check_class_methods, check_flag_param
from cq_measure.checks.functions.function_checks import (
    check_complexity,
    check_function_lines,
    check_nesting,
    check_params,
)

CHECKS = {
    "function-lines": check_function_lines,
    "nesting": check_nesting,
    "complexity": check_complexity,
    "params": check_params,
    "flag-param": check_flag_param,
    "class-methods": check_class_methods,
}
