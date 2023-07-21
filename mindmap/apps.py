"""
Mind Map Django application initialization.
"""

from django.apps import AppConfig


class MindMapConfig(AppConfig):
    """
    Configuration for the Mind Map Django application.
    """
    name = "mindmap"
    plugin_app = {
        "settings_config": {
            "lms.djangoapp": {
                "common": {"relative_path": "settings.common"},
                "test": {"relative_path": "settings.test"},
                "production": {"relative_path": "settings.production"},
            },
            "cms.djangoapp": {
                "common": {"relative_path": "settings.common"},
                "test": {"relative_path": "settings.test"},
                "production": {"relative_path": "settings.production"},
            },
        }
    }
