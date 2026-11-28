"""Checks for section 2: directories."""

from cq_measure.structure.directories.dir_depth import check_dir_depth
from cq_measure.structure.directories.dir_name_case import check_dir_name_case
from cq_measure.structure.directories.dir_size import check_dir_files, check_dir_subdirs
from cq_measure.structure.directories.generated_placement import (
    check_generated_placement,
)
from cq_measure.structure.directories.package_by_layer import check_package_by_layer
from cq_measure.structure.directories.root import check_root_files, check_root_source
from cq_measure.structure.directories.script_placement import check_script_placement
from cq_measure.structure.directories.single_child_dir import check_single_child_dir
from cq_measure.structure.directories.vague_name import check_vague_name

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
