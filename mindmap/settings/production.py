"""
Settings for the Mind Map plugin.
"""


def plugin_settings(settings):
    """
    Read / Update necessary project settings for production envs.
    """
    # AWS S3 settings
    settings.AWS_SECRET_ACCESS_KEY = getattr(settings, "ENV_TOKENS", {}).get(
        "AWS_SECRET_ACCESS_KEY",
        settings.AWS_SECRET_ACCESS_KEY
    )
    settings.AWS_ACCESS_KEY_ID = getattr(settings, "ENV_TOKENS", {}).get(
        "AWS_ACCESS_KEY_ID",
        settings.AWS_ACCESS_KEY_ID
    )
    settings.AWS_DEFAULT_ACL = getattr(settings, "ENV_TOKENS", {}).get(
        "AWS_DEFAULT_ACL",
        settings.AWS_DEFAULT_ACL
    )
    settings.MINDMAP_BLOCK_STORAGE = getattr(settings, "ENV_TOKENS", {}).get(
        "MINDMAP_BLOCK_STORAGE",
        settings.MINDMAP_BLOCK_STORAGE
    )
