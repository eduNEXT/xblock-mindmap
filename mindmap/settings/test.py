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

# Mind Map plugin settings
MINDMAP_XMODULE_BACKEND = 'mindmap.edxapp_wrapper.backends.xmodule_p_v1'
MINDMAP_STUDENT_MODULE_BACKEND = 'mindmap.edxapp_wrapper.backends.student_p_v1'
