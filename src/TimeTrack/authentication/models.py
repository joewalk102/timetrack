from django.contrib.auth.models import AbstractUser
from django.db import models


class TTUser(AbstractUser):
    """
    Custom user model for TimeTrack application.
    Inherits from Django's AbstractUser to allow for future customization.
    """

    timezone = models.CharField(
        max_length=50, default="UTC", help_text="User's preferred timezone"
    )
    dark_mode = models.BooleanField(
        default=False, help_text="Enable dark mode for the user interface"
    )
