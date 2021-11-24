"""Command-line interface."""
import click


@click.command()
@click.version_option()
def main() -> None:
    """Imiit Student Bot."""


if __name__ == "__main__":
    main(prog_name="imiit-student-bot")  # pragma: no cover
