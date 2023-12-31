"""
Student module generalized definitions.
"""

from importlib import import_module
from django.conf import settings


def get_anonymous_user_id_function(*args, **kwargs):
    """Get modulestore object."""

    backend_function = settings.MINDMAP_STUDENT_MODULE_BACKEND
    backend = import_module(backend_function)

    return backend.get_user_by_anonymous_id(*args, **kwargs)


def get_student_module_function():
    """Get StudentModule model."""

    backend_function = settings.MINDMAP_STUDENT_MODULE_BACKEND
    backend = import_module(backend_function)

    return backend.get_student_module()


student_module = get_student_module_function
user_by_anonymous_id = get_anonymous_user_id_function
