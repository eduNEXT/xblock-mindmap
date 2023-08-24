"""
Utilities for mindmap app.
"""
import datetime
import pytz


def _(text):
    """
    Dummy `gettext` replacement to make string extraction tools scrape strings marked for translation.
    """
    return text


def utcnow():
    """
    Get current date and time in UTC.

    Returns:
        datetime.datetime: Current date and time in UTC.
    """
    return datetime.datetime.now(tz=pytz.utc)
