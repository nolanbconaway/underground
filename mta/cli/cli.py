"""Create nested CLI tools."""

import click
from mta.cli import stops


@click.group()
def entry_point():
    """Command line handlers for MTA realtime data."""


entry_point.add_command(stops.main, name="stops")
