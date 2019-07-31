"""Command line interface."""

import argparse
import itertools
import os
import sys

import dotenv

from . import dateutils, metadata
from .mta import get_feed_stops

parser = argparse.ArgumentParser()

"""
APIKEY -- env
ROUTE 
STOP
"""
parser.add_argument("route", help="Route id.", choices=metadata.VALID_ROUTES)

parser.add_argument(
    "-f",
    "--format",
    default="%H:%M",
    type=str,
    dest="format",
    help="strftime format for stop times.",
)

parser.add_argument(
    "-e",
    "--epoch",
    action="store_true",
    dest="epoch",
    help="Option to print times as unix timestamps. If set --format will be ignored.",
)

parser.add_argument(
    "--retries",
    default=100,
    type=int,
    dest="retries",
    help="Retry attempts in case of API connection failure. Default 100.",
)

parser.add_argument(
    "--api-key",
    default=None,
    dest="api_key",
    help="MTA API key. Will be read from $API_KEY if not provided.",
)


def main():
    """CLI main function."""
    # load env
    if os.path.exists(".env"):
        dotenv.load_dotenv()

    # parse args
    args = parser.parse_args()

    if args.api_key:
        api_key = args.api_key
    else:
        api_key = os.getenv("API_KEY")
        if not api_key:
            sys.exit("No API_KEY set!")

    # get feed data
    stops = get_feed_stops(
        api_key=api_key,
        feed_id=metadata.ROUTE_FEED_MAP.get(args.route),
        retries=args.retries,
    ).get(args.route, dict())

    if args.epoch:
        format_fun = dateutils.datetime_to_epoch
    else:
        format_fun = lambda x: x.strftime(args.format)

    for stop_id, departures in stops.items():
        departures_formatted = map(str, map(format_fun, sorted(departures)))
        print(f"""{stop_id}  {' '.join(departures_formatted)}""")


if __name__ == "__main__":
    main()
