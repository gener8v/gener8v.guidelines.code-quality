"""Checks for section 1: files."""

from cq_measure.checks.files.concepts import check_name_matches_export, check_one_concept
from cq_measure.checks.files.file_lines import check_file_lines
from cq_measure.checks.files.file_naming import check_file_name_case, check_role_suffix

CHECKS = {
    "file-lines": check_file_lines,
    "one-concept": check_one_concept,
    "name-matches-export": check_name_matches_export,
    "role-suffix": check_role_suffix,
    "file-name-case": check_file_name_case,
}
