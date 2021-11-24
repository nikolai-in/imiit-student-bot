"""Command-line interface."""
import click


@click.command()
@click.argument(
    "token",
    type=str,
)
@click.version_option()
def main(token: str) -> None:
    """Imiit Student Bot.

    Args:
        token: Bot authentication token.
    """


if __name__ == "__main__":
    main(prog_name="imiit-student-bot")  # pragma: no cover
