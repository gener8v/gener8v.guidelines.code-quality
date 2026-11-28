"""The core name of a file: its stem without test markers."""

from __future__ import annotations

from cq_measure.codebase import is_test_file, test_subject


def core_name(source) -> str:
    """Return the stem without test markers: `invoice_test.py` gives `invoice`."""
    subject = test_subject(source.path) if is_test_file(source.path) else None
    return subject or source.stem
