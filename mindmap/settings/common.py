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
    settings.AWS_DEFAULT_ACL = None
    settings.MINDMAP_BLOCK_STORAGE = {
        "storage_class": "storages.backends.s3boto3.S3Boto3Storage",
        "settings": {
            "bucket_name": "CHANGE-ME",
        },
    }
