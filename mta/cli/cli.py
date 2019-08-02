"""Create nested CLI tools."""
import os

import click

from mta.cli import image, stops


@click.group()
def entry_point():
    """Command line handlers for MTA realtime data."""
    pass


entry_point.add_command(stops.main, name="stops")
entry_point.add_command(image.main, name="image")
