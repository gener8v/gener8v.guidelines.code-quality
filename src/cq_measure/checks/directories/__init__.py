"""Checks for section 2: directories."""

from cq_measure.checks.directories.domain_first import check_package_by_layer
from cq_measure.checks.directories.layout import check_generated_placement, check_script_placement, check_single_child_dir
from cq_measure.checks.directories.naming import check_dir_name_case, check_vague_name
from cq_measure.checks.directories.root import check_root_files, check_root_source
from cq_measure.checks.directories.size import check_dir_depth, check_dir_files, check_dir_subdirs

CHECKS = {
    "root-files": check_root_files,
    "root-source": check_root_source,
    "dir-files": check_dir_files,
    "dir-subdirs": check_dir_subdirs,
    "dir-depth": check_dir_depth,
    "vague-name": check_vague_name,
    "package-by-layer": check_package_by_layer,
    "single-child-dir": check_single_child_dir,
    "generated-placement": check_generated_placement,
    "script-placement": check_script_placement,
    "dir-name-case": check_dir_name_case,
}
