"""
Settings for the Mind Map plugin.
"""


def plugin_settings(settings):
    """
    Read / Update necessary common project settings.
    """
    settings.MINDMAP_XMODULE_BACKEND = 'mindmap.edxapp_wrapper.backends.xmodule_p_v1'
    settings.MINDMAP_STUDENT_MODULE_BACKEND = 'mindmap.edxapp_wrapper.backends.student_p_v1'
