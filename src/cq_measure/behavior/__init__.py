"""Checks for the behavior rules that a tool can measure (sections 11 to 18)."""

from cq_measure.behavior.debug_output import check_debug_output
from cq_measure.behavior.secret_literal import check_secret_literal
from cq_measure.behavior.swallowed_error import check_swallowed_error
from cq_measure.behavior.todo_comments import check_todo_without_issue
from cq_measure.behavior.type_escape import check_type_escape

CHECKS = {
    "type-escape": check_type_escape,
    "swallowed-error": check_swallowed_error,
    "todo-without-issue": check_todo_without_issue,
    "secret-literal": check_secret_literal,
    "debug-output": check_debug_output,
}
