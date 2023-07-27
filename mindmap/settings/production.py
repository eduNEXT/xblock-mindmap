"""
Settings for the Mind Map plugin.
"""


def plugin_settings(settings):
    """
    Read / Update necessary project settings for production envs.
    """
    # AWS S3 settings
    settings.AWS_SECRET_ACCESS_KEY_ID = getattr(settings, "ENV_TOKENS", {}).get(
        "AWS_SECRET_ACCESS_KEY_ID",
        settings.AWS_SECRET_ACCESS_KEY_ID
    )
    settings.AWS_ACCESS_KEY_ID = getattr(settings, "ENV_TOKENS", {}).get(
        "AWS_ACCESS_KEY_ID",
        settings.AWS_ACCESS_KEY_ID
    )
    settings.AWS_BUCKET_NAME = getattr(settings, "ENV_TOKENS", {}).get(
        "AWS_BUCKET_NAME",
        settings.AWS_BUCKET_NAME
    )
