from collections import defaultdict
from datetime import datetime, date, timedelta, UTC
from logging import getLogger

from django.utils import timezone

from library.time_helpers.localization import convert_to_user_time
from project.models import Project, TimeEntry

log = getLogger(__name__)


class EntriesOverTime:

    @staticmethod
    def entry_time_by_day(
        projects: list[Project],
        start_day: date,
        end_day: date,
    ) -> list[dict]:
        """
        Process the entries to calculate total time spent per day.
        """
        time_entries = (
            TimeEntry.objects.filter(
                project__in=projects,
                start_time__gte=start_day - timedelta(days=2),
                end_time__lte=end_day + timedelta(days=2),
            )
            .order_by("start_time")
            .all()
        )

        days_desired = []
        cur_day = start_day
        while cur_day <= end_day:
            days_desired.append(cur_day)
            cur_day += timedelta(days=1)

        daily_data = []
        for day in days_desired:
            seconds = 0
            day_by_project = defaultdict(int)
            for record in time_entries:
                # Total time for the day
                record_date = record.start_time
                user_date = convert_to_user_time(record_date, record.project.owner)
                if user_date.date() == day:
                    delta = record.end_time - record.start_time
                    seconds += delta.total_seconds()
                    day_by_project[record.project.name] += delta.total_seconds()
                elif user_date.date() > day:
                    # Results should be ordered by date, so we can break early
                    break

            daily_data.append(
                {
                    "day": day,
                    "hours": round(seconds / 3600, 1),
                    "by_project": {
                        project: round(secs / 3600, 1)
                        for project, secs in day_by_project.items()
                    },
                }
            )
        return daily_data

    @staticmethod
    def entry_time_by_month(
        projects: list[Project],
        desired_year: int | None = None,
    ) -> list[dict]:
        """
        Process the entries to calculate total time spent per month.
        """
        current_year = desired_year or timezone.now().year
        time_entries = []
        for project in projects:
            project_entries = project.time_entries.filter(
                start_time__year=current_year
            ).all()
            time_entries.extend(project_entries)

        monthly_data = []
        for month in range(1, 13):
            seconds = 0
            for record in time_entries:
                # Total time for the month
                if record.start_time.month == month:
                    delta = record.end_time - record.start_time
                    seconds += delta.total_seconds()
            seconds = (month * 5) % 50  # Sample data
            monthly_data.append(
                {
                    "month": datetime(current_year, month, 1).strftime("%B"),
                    "hours": seconds // 3600,
                }
            )
        return monthly_data
