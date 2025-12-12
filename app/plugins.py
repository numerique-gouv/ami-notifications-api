from advanced_alchemy.extensions.litestar import SQLAlchemyPlugin
from litestar.channels import ChannelsPlugin
from litestar.channels.backends.memory import MemoryChannelsBackend

from app.database import alchemy_config

alchemy = SQLAlchemyPlugin(config=alchemy_config)
channels = ChannelsPlugin(
    channels=["notification_events"], backend=MemoryChannelsBackend(history=0)
)
