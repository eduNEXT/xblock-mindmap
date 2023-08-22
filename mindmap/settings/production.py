"""
Settings for the Mind Map plugin.
"""


def plugin_settings(settings): # pylint: disable=unused-argument
    """
    Read / Update necessary project settings for production envs.
    """
    settings.MINDMAP_XMODULE_BACKEND = getattr(settings, "ENV_TOKENS", {}).get(
        "MINDMAP_XMODULE_BACKEND",
        settings.MINDMAP_XMODULE_BACKEND
    )
    settings.MINDMAP_STUDENT_MODULE_BACKEND = getattr(settings, "ENV_TOKENS", {}).get(
        "MINDMAP_STUDENT_MODULE_BACKEND",
        settings.MINDMAP_STUDENT_MODULE_BACKEND
    )
