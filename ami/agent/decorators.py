from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import login_required, user_passes_test


def agent_login_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None):
    def check(user):
        return getattr(user, "agent", None) is not None

    def actual_decorator(f):
        return login_required(
            user_passes_test(
                check,
                login_url=login_url,
                redirect_field_name=redirect_field_name,
            )(f),
            login_url=login_url,
            redirect_field_name=redirect_field_name,
        )

    if function:
        return actual_decorator(function)
    return actual_decorator
