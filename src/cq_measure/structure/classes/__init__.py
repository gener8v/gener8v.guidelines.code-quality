"""Checks for section 4: classes."""

from cq_measure.structure.classes.all_classes import all_classes
from cq_measure.structure.classes.class_methods import check_class_methods
from cq_measure.structure.classes.file_classes import classes_of

CHECKS = {"class-methods": check_class_methods}

__all__ = [
    "CHECKS",
    "all_classes",
    "classes_of",
]
