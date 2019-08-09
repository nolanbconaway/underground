"""Command line interface."""

import datetime
import os

import click
import dotenv
import pytz

from underground import dateutils, metadata
from underground.mta import get_stops


@click.command()
@click.argument("route", nargs=1, type=click.Choice(metadata.VALID_ROUTES))
@click.option(
    "-f",
    "--format",
    "fmt",
    default="%H:%M",
    type=str,
    help="strftime format for stop times.",
)
@click.option(
    "-e",
    "--epoch",
    "epoch",
    default=False,
    is_flag=True,
    type=bool,
    help="Option to print times as unix timestamps. If set --format will be ignored.",
)
@click.option(
    "-r",
    "--retries",
    "retries",
    default=100,
    type=int,
    help="Retry attempts in case of API connection failure. Default 100.",
)
@click.option(
    "--api-key",
    "api_key",
    default=None,
    help="MTA API key. Will be read from $API_KEY if not provided.",
)
@click.option(
    "-t",
    "--timezone",
    "timezone",
    default=dateutils.DEFAULT_TIMEZONE,
    help="Output timezone. Ignored if --epoch. Default to NYC time.",
)
def main(route, fmt, epoch, retries, api_key, timezone):
    """Print out train departure times for all stops on a subway line."""
    # get api key from env if not provided
    if api_key is None:
        if os.path.exists(".env"):
            dotenv.load_dotenv()

        api_key = os.getenv("MTA_API_KEY")

        if api_key is None:
            raise click.ClickException("No MTA_API_KEY set!")

    # get feed data
    stops = get_stops(
        api_key=api_key, feed_id=metadata.ROUTE_FEED_MAP.get(route), retries=retries
    ).get(route, dict())

    if epoch:
        format_fun = dateutils.datetime_to_epoch
    else:
        format_fun = lambda x: x.astimezone(pytz.timezone(timezone)).strftime(fmt)

    for stop_id, departures in stops.items():
        departures_formatted = map(str, map(format_fun, sorted(departures)))
        click.echo(f"""{stop_id}  {' '.join(departures_formatted)}""")


if __name__ == "__main__":
    main()
