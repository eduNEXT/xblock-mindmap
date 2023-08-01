"""
Settings for the Mind Map plugin for testing purposes.
"""

# SECURITY WARNING: keep the secret key used in production secret!
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "default.db",
        "USER": "",
        "PASSWORD": "",
        "HOST": "",
        "PORT": "",
    },
    "read_replica": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "read_replica.db",
        "USER": "",
        "PASSWORD": "",
        "HOST": "",
        "PORT": "",
    },
}


INSTALLED_APPS = (
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "mindmap",
)


SECRET_KEY = "not-so-secret-key"

# Internationalization
# https://docs.djangoproject.com/en/2.22/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_TZ = True

# AWS S3 settings
AWS_ACCESS_KEY_ID = "test-aws-access-key-id"
<<<<<<< HEAD
AWS_SECRET_ACCESS_KEY = "test-aws-secret-access-key"
=======
<<<<<<< HEAD
AWS_SECRET_ACCESS_KEY = "test-aws-secret-access-key-id"
=======
AWS_SECRET_ACCESS_KEY = "test-aws-secret-access-key"
>>>>>>> 283f39d703da8728e4b410d5deb0b52841183c29
>>>>>>> afc9e74... fix: update with main branch
FILE_UPLOAD_STORAGE_BUCKET_NAME = "test-file-upload-storage-bucket-name"
