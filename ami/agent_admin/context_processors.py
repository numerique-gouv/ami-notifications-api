import json
from dataclasses import dataclass
from typing import Any

from django.contrib.messages.context_processors import messages as django_messages
from django.contrib.messages.storage.base import Message as DjangoMessage


@dataclass
class Message:
    message: dict[str, Any]
    level: int
    level_tag: str
    extra_tags: str
    tags: str

    @classmethod
    def from_message(cls, message: DjangoMessage) -> "Message":
        try:
            data = json.loads(message.message)
        except json.JSONDecodeError:
            data = {"title": message.message}
        return cls(
            message=data,
            level=message.level,
            level_tag=message.level_tag,
            extra_tags=message.extra_tags,
            tags=message.tags,
        )


def messages(request):
    result = django_messages(request)
    result["messages"] = [
        Message.from_message(msg) for msg in result["messages"] if isinstance(msg, DjangoMessage)
    ]
    return result
