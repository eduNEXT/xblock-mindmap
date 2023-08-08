"""
Settings for the Mind Map plugin.
"""


def plugin_settings(settings):
    """
    Read / Update necessary common project settings.
    """
    # AWS S3 settings
    settings.MINDMAP_BLOCK_STORAGE = {
        "storage_class": "storages.backends.s3boto3.S3Boto3Storage",
        "settings": {
            "bucket_name": "CHANGE-ME",
        },
    }
