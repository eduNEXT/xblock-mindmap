"""
Utilities for mindmap app.
"""
from django.conf import settings
from django.core.files.storage import default_storage, get_storage_class


def get_mindmap_storage():
    """
    Return the storage for mindmap files.
    """
    mindmap_storage_settings = getattr(settings, 'MINDMAP_BLOCK_STORAGE', None)

    if not mindmap_storage_settings:
        return default_storage

    storage_class_import_path = mindmap_storage_settings.get('storage_class', None)
    storage_settings = mindmap_storage_settings.get('settings', {})

    storage_class = get_storage_class(storage_class_import_path)

    storage = storage_class(**storage_settings)

    return storage
