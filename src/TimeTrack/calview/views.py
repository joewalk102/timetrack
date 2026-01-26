from datetime import timedelta, date
from logging import getLogger

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from library.project_operations.data_processing import EntriesOverTime
from library.time_helpers.localization import get_user_now
from project.models import Project

log = getLogger(__name__)


@login_required
def home(request):
    return render(
        request,
        "calview/home.html",
    )


@login_required
def hx_weekly_calendar_data(request):
    projects = Project.objects.filter(owner=request.user).all()

    # get Monday of the current week by default
    week_offset = int(request.GET.get("week_offset", 0))
    user_now = get_user_now(request.user)
    monday = user_now - timedelta(days=user_now.weekday())
    week_starting: date = monday.date() + timedelta(days=week_offset * 7)
    log.info(f"Week starting date: {week_starting}")

    week_days = EntriesOverTime.entry_time_by_day(
        projects=list(projects),
        start_day=week_starting,
        end_day=(week_starting + timedelta(days=6)),
    )
    context = {
        "projects": projects,
        "current_year": week_starting.year,
        "current_month": week_starting.month,
        "date_range": [int(week_offset) + 1, int(week_offset) - 1],
        "offset": [week_offset - 1, week_offset + 1],
        "start_date": week_starting,
        "end_date": week_starting + timedelta(days=6),
        "week_days": week_days,
    }
    return render(
        request,
        "calview/htmx/weekly_calendar.html",
        context=context,
    )
