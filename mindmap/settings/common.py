"""
Settings for the Mind Map plugin.
"""


def plugin_settings(settings):
    """
    Read / Update necessary common project settings.
    """
    # AWS S3 settings
    settings.AWS_ACCESS_KEY_ID = "CHANGE-ME"
    settings.AWS_SECRET_ACCESS_KEY = "CHANGE-ME"
    settings.FILE_UPLOAD_STORAGE_BUCKET_NAME = "CHANGE-ME"
