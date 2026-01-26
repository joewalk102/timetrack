from datetime import datetime

import pytz
from django.utils import timezone

from authentication.models import TTUser


def convert_to_user_time(dt: datetime, user: TTUser) -> datetime:
    """
    Convert a datetime object to the user's local time zone.

    Args:
        dt (datetime): The datetime object to convert.
        user (User): The user object containing time zone information.

    Returns:
        datetime: The converted datetime object in the user's local time zone.
    """
    if not hasattr(user, "timezone") or not user.timezone:
        return dt  # Return original datetime if no timezone is set

    user_tz = pytz.timezone(user.timezone)
    if dt.tzinfo is None:
        # Assume dt is in UTC if it has no timezone info
        dt = pytz.utc.localize(dt)

    return dt.astimezone(user_tz)


def get_user_now(user):
    """
    Get the current time in the user's local time zone.

    Args:
        user (User): The user object containing time zone information.
    Returns:
        datetime: The current datetime in the user's local time zone.
    """
    now_utc = timezone.now()
    return convert_to_user_time(now_utc, user)
