"""Checks for section 1: files."""

from cq_measure.structure.files.concept_names import normalize
from cq_measure.structure.files.file_lines import check_file_lines
from cq_measure.structure.files.file_name_case import check_file_name_case
from cq_measure.structure.files.name_matches_export import check_name_matches_export
from cq_measure.structure.files.one_concept import check_one_concept
from cq_measure.structure.files.role_suffix import check_role_suffix

CHECKS = {
    "file-lines": check_file_lines,
    "one-concept": check_one_concept,
    "name-matches-export": check_name_matches_export,
    "role-suffix": check_role_suffix,
    "file-name-case": check_file_name_case,
}

__all__ = [
    "CHECKS",
    "normalize",
]
