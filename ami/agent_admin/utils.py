from ami.agent.models import Agent
from ami.agent_admin.models import AuditEntry


def audit(action, author, extra_data):
    action_type, action_code = action.split(":", 1)

    if "agent" in extra_data:
        agent = extra_data["agent"]
        extra_data["agent_id"] = str(agent.id)
        extra_data["agent_first_name"] = agent.user.first_name
        extra_data["agent_last_name"] = agent.user.last_name
        extra_data["agent_email"] = agent.user.email
        extra_data["agent_proconnect_sub"] = agent.proconnect_sub
        del extra_data["agent"]

    for key in ["old_role", "new_role"]:
        if key in extra_data:
            extra_data[f"{key}_name"] = Agent.Role(extra_data[key]).label

    if "user" in extra_data:
        user = extra_data["user"]
        extra_data["user_id"] = str(user.id)
        extra_data["user_fc_hash"] = str(user.fc_hash)
        del extra_data["user"]

    return AuditEntry.objects.create(
        author=author,
        author_first_name=author.user.first_name,
        author_last_name=author.user.last_name,
        author_email=author.user.email,
        author_proconnect_sub=author.proconnect_sub,
        action_type=action_type,
        action_code=action_code,
        extra_data=extra_data,
    )
