"""
Xmodule definitions for Open edX Palm release.
"""
from xmodule.util.duedate import get_extended_due_date


def get_extended_due_date_util(*args, **kwargs):
    """
    Get extended due date for the problem.

    Returns:
        datetime.datetime: Extended due date for the problem.
    """
    return get_extended_due_date(*args, **kwargs)
