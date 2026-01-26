from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone

from library.project_operations.data_processing import EntriesOverTime
from project.models import Project


@login_required()
def home(request):
    projects = Project.objects.filter(owner=request.user).all()
    return render(
        request,
        "project/home.html",
        context={"projects": projects},
    )


@login_required
def project_detail(request, project_id):
    """
    Displays project details with monthly time tracking breakdown for the current year.
    """
    project = Project.objects.get(id=project_id)

    current_year = request.GET.get("year", timezone.now().year)
    monthly_data = EntriesOverTime.entry_time_by_month(
        projects=[project],
        desired_year=int(current_year),
    )

    total_hours = sum(item["hours"] for item in monthly_data)

    context = {
        "project": project,
        "current_year": current_year,
        "monthly_data": monthly_data,
        "total_hours": total_hours,
    }

    return render(request, "project/project_detail.html", context)


@login_required
def hx_list_item(request, project_id):
    project = Project.objects.get(id=project_id)
    if request.GET.get("action") == "stop":
        project.stop_timer()
    elif request.GET.get("action") == "start":
        project.start_timer()
    return render(
        request,
        "project/htmx/list_item.html",
        context={"project": project},
    )
