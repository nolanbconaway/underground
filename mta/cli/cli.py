"""Create nested CLI tools."""
import os

import click

from mta.cli import stops


@click.group()
def entry_point():
    """Command line handlers for MTA realtime data."""
    pass


entry_point.add_command(stops.main, name="stops")
