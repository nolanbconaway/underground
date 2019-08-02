"""Create nested CLI tools."""
import os

import click

from mta.cli import stops


@click.group()
def entry_point():
    """The base group for MTA CLI."""
    pass


entry_point.add_command(stops.main, name="stops")
