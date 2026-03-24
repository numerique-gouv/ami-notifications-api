from django.shortcuts import render

from ami.agent.decorators import agent_login_required


@agent_login_required
def home(request):
    return render(request, "agent_admin/home.html", {})


def login(request):
    return render(request, "agent_admin/login.html", {})
