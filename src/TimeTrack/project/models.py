from logging import getLogger

from django.db import models
from django.utils import timezone

from library.time_helpers.localization import convert_to_user_time

log = getLogger(__name__)


# Create your models here.
class Project(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(
        "authentication.TTUser",
        on_delete=models.CASCADE,
        related_name="projects",
        db_index=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @property
    def is_active(self):
        return self.time_entries.filter(end_time__isnull=True).exists()

    def start_timer(self):
        if not self.is_active:
            TimeEntry.objects.create(
                project=self,
                user=self.owner,
                start_time=timezone.now(),
            )

    def stop_timer(self):
        entry = self.time_entries.filter(end_time__isnull=True).first()
        entry.end_time = timezone.now()
        entry.save()

    @property
    def last_started_at(self):
        last_entry = self.time_entries.order_by("-start_time").first()
        if not last_entry:
            return None
        time_last_started = last_entry.start_time
        log.info(f"Last started at (UTC): {time_last_started}")
        user_last_started = convert_to_user_time(time_last_started, self.owner)
        log.info(f"Last started at (User Time): {user_last_started}")
        return user_last_started.strftime("%Y-%m-%d %I:%M:%S %p")


class TimeEntry(models.Model):
    id = models.AutoField(primary_key=True)
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="time_entries",
        db_index=True,
    )
    user = models.ForeignKey(
        "authentication.TTUser",
        on_delete=models.CASCADE,
        related_name="time_entries",
        db_index=True,
    )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, db_index=True)

    def __str__(self):
        return f"{self.user.username} - {self.project.name} ({self.start_time} to {self.end_time})"
