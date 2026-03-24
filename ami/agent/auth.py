from django.utils.timezone import now
from mozilla_django_oidc.auth import OIDCAuthenticationBackend

from ami.agent.models import Agent


class AgentAuthenticationBackend(OIDCAuthenticationBackend):
    def filter_users_by_claims(self, claims):
        sub = claims.get("sub")
        if not sub:
            return self.UserModel.objects.none()

        if self.UserModel.objects.filter(agent__proconnect_sub=sub):
            return self.UserModel.objects.filter(agent__proconnect_sub=sub)

        username = self.get_username(claims)
        return self.UserModel.objects.filter(username=username)

    def create_agent(self, user, claims):
        Agent.objects.create(user=user, proconnect_sub=claims["sub"], proconnect_last_login=now())

    def create_user(self, claims):
        user = super(AgentAuthenticationBackend, self).create_user(claims)

        user.first_name = claims.get("given_name", "")
        user.last_name = claims.get("usual_name", "")
        user.email = claims.get("email", "")
        user.save()

        self.create_agent(user, claims)

        return user

    def update_user(self, user, claims):
        user.first_name = claims.get("given_name", "")
        user.last_name = claims.get("usual_name", "")
        user.email = claims.get("email", "")
        user.save()

        if not hasattr(user, "agent"):
            self.create_agent(user, claims)
        else:
            Agent.objects.filter(user=user).update(proconnect_last_login=now(), updated_at=now())

        return user
