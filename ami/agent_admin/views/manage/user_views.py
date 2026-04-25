from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from ami.agent.decorators import (
    agent_login_required,
    role_admin_required,
)
from ami.agent_admin.forms import UserSearchForm
from ami.user.models import User


@agent_login_required
@role_admin_required
def search_user(request):
    if request.method == "POST":
        form = UserSearchForm(data=request.POST)
        if form.is_valid():
            if form.user:
                return redirect(reverse("agent-admin:manage:detail-user", args=[form.user.id]))
    else:
        form = UserSearchForm()
    context = {
        "form": form,
    }
    return render(request, "agent_admin/manage/search_user.html", context)


@agent_login_required
@role_admin_required
def detail_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    form = UserSearchForm(initial={"fc_hash": user.fc_hash})
    context = {
        "form": form,
        "ami_user": user,
    }
    return render(request, "agent_admin/manage/detail_user.html", context)


@agent_login_required
@role_admin_required
@require_http_methods(["POST"])
@csrf_exempt
def delete_user(request, user_id):
    return redirect(reverse("agent-admin:manage:search-user"))
