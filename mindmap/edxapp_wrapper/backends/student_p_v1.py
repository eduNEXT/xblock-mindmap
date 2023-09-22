"""
Student module definitions for Open edX Palm release.
"""
# pylint: disable=import-error
from common.djangoapps.student.models import user_by_anonymous_id
from lms.djangoapps.courseware.models import StudentModule


def get_user_by_anonymous_id(*args, **kwargs):
    """
    Get user by anonymous id.

    Returns:
        User: User object.
    """
    return user_by_anonymous_id(*args, **kwargs)


def get_student_module():
    """
    Get StudentModule model.

    Returns:
        StudentModule: StudentModule object.
    """
    return StudentModule
