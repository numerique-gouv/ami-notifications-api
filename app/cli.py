import anyio
import click
from advanced_alchemy.extensions.litestar.providers import create_service_provider
from click import Group
from litestar import Litestar
from litestar.plugins import CLIPluginProtocol

from app.database import alchemy_config
from app.services.scheduled_notification import ScheduledNotificationService
from app.utils import generate_identity_tokens_in_file


class CLIPlugin(CLIPluginProtocol):
    def on_cli_init(self, cli: Group) -> None:
        @cli.command()
        def publish_scheduled_notifications(app: Litestar) -> None:  # type: ignore[reportUnusedFunction]
            anyio.run(_publish_scheduled_notifications, app)

        @cli.command()
        def delete_published_scheduled_notifications() -> None:  # type: ignore[reportUnusedFunction]
            anyio.run(_delete_published_scheduled_notifications)

        @cli.command()
        @click.argument("input_file_path")
        @click.argument("output_file_path")
        def generate_identity_tokens(input_file_path: str, output_file_path: str) -> None:  # type: ignore[reportUnusedFunction]
            generate_identity_tokens_in_file(input_file_path, output_file_path)


async def _publish_scheduled_notifications(app: Litestar) -> None:
    async with app.lifespan():
        provide_scheduled_notifications_service = create_service_provider(
            ScheduledNotificationService
        )
        async with alchemy_config.get_session() as db_session:
            scheduled_notifications_service: ScheduledNotificationService = await anext(
                provide_scheduled_notifications_service(db_session)
            )
            await scheduled_notifications_service.publish_scheduled_notifications(app)


async def _delete_published_scheduled_notifications() -> None:
    provide_scheduled_notifications_service = create_service_provider(ScheduledNotificationService)
    async with alchemy_config.get_session() as db_session:
        scheduled_notifications_service: ScheduledNotificationService = await anext(
            provide_scheduled_notifications_service(db_session)
        )
        await scheduled_notifications_service.delete_published_scheduled_notifications()
