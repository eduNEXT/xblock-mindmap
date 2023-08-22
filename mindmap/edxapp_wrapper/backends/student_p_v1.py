"""
Student module definitions for Open edX Palm release.
"""

from common.djangoapps.student.models import user_by_anonymous_id


def get_user_by_anonymous_id(*args, **kwargs):
    """
    Get user by anonymous id.

    Returns:
        User: User object.
    """
    return user_by_anonymous_id(*args, **kwargs)
