"""Get upcoming stops along a train route."""

import datetime

import click
import pytz

from underground import metadata
from underground.models import SubwayFeed


def datetime_to_epoch(dttm: datetime.datetime) -> int:
    """Return a unix timestmap from a datetime."""
    return int(dttm.astimezone(pytz.timezone("UTC")).timestamp())


@click.command()
@click.argument("route", nargs=1, type=click.Choice(metadata.VALID_ROUTES))
@click.option(
    "-f",
    "--format",
    "fmt",
    default="%H:%M",
    type=str,
    help="strftime format for stop times. Use `epoch` for a unix timestamp.",
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
    help="MTA API key. Will be read from $MTA_API_KEY if not provided.",
)
@click.option(
    "-t",
    "--timezone",
    "timezone",
    default=metadata.DEFAULT_TIMEZONE,
    help="Output timezone. Ignored if --epoch. Default to NYC time.",
)
def main(route, fmt, retries, api_key, timezone):
    """Print out train departure times for all stops on a subway line."""
    stops = (
        SubwayFeed.get(api_key=api_key, route_or_url=route, retries=retries)
        .extract_stop_dict(timezone=timezone)
        .get(route, dict())
    )

    # figure out how to format it
    if fmt == "epoch":
        format_fun = datetime_to_epoch
    else:
        format_fun = lambda x: x.strftime(fmt)

    # echo the result
    for stop_id, departures in stops.items():
        departures_formatted = map(str, map(format_fun, sorted(departures)))
        click.echo(f"""{stop_id} {' '.join(departures_formatted)}""")


if __name__ == "__main__":
    main()
