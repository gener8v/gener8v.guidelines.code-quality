"""Checks for section 4: functions."""

from cq_measure.structure.functions.approximation.script_functions import (
    ScriptFunction,
    find_functions,
    match_brackets,
)
from cq_measure.structure.functions.complexity import check_complexity
from cq_measure.structure.functions.file_functions import functions_of
from cq_measure.structure.functions.flag_param import check_flag_param
from cq_measure.structure.functions.function_lines import check_function_lines
from cq_measure.structure.functions.nesting import check_nesting
from cq_measure.structure.functions.params import check_params
from cq_measure.structure.functions.python_functions import (
    FUNCTIONS,
    has_logic,
    parameters,
)

CHECKS = {
    "function-lines": check_function_lines,
    "nesting": check_nesting,
    "complexity": check_complexity,
    "params": check_params,
    "flag-param": check_flag_param,
}

__all__ = [
    "CHECKS",
    "FUNCTIONS",
    "ScriptFunction",
    "find_functions",
    "functions_of",
    "has_logic",
    "match_brackets",
    "parameters",
]
