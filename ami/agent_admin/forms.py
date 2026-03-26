from django.forms import modelformset_factory

from ami.agent.models import Agent

AgentFormSet = modelformset_factory(Agent, fields=["role"], extra=0)
