"""
Xmodule generalized definitions.
"""

from importlib import import_module
from django.conf import settings


def get_extended_due_date_function(*args, **kwargs):
    """Get modulestore object."""

    backend_function = settings.MINDMAP_XMODULE_BACKEND
    backend = import_module(backend_function)

    return backend.get_extended_due_date_util(*args, **kwargs)


get_extended_due_date = get_extended_due_date_function
