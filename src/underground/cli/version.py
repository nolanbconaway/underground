"""Print the underground version."""

import click

from underground import __version__


@click.command()
def main():
    """Print the underground version."""
    click.echo(__version__)


if __name__ == "__main__":
    main()
