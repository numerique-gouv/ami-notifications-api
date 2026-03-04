import click
from click import Group
from litestar.plugins import CLIPluginProtocol

from app.utils import generate_identity_tokens_in_file


class CLIPlugin(CLIPluginProtocol):
    def on_cli_init(self, cli: Group) -> None:
        @cli.command()
        @click.argument("input_file_path")
        @click.argument("output_file_path")
        def generate_identity_tokens(input_file_path: str, output_file_path: str) -> None:  # type: ignore[reportUnusedFunction]
            generate_identity_tokens_in_file(input_file_path, output_file_path)
