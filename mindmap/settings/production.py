"""
Settings for the Mind Map plugin.
"""


def plugin_settings(settings):
    """
    Read / Update necessary project settings for production envs.
    """
    # AWS S3 settings
    settings.MINDMAP_BLOCK_STORAGE = getattr(settings, "ENV_TOKENS", {}).get(
        "MINDMAP_BLOCK_STORAGE",
        settings.MINDMAP_BLOCK_STORAGE
    )
