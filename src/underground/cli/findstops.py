"""Get upcoming stops along a train route."""

import csv
import io
import json
import zipfile
from collections.abc import Generator

import click
import requests

# url to the zip file containing MTA metadata
# see "Static GTFS Data" at https://www.mta.info/developers
DATA_URLS = {
    # subway
    "subway": "http://web.mta.info/developers/data/nyct/subway/google_transit.zip",
    # buses
    "buses_bx": "https://rrgtfsfeeds.s3.amazonaws.com/gtfs_bx.zip",
    "buses_bk": "https://rrgtfsfeeds.s3.amazonaws.com/gtfs_b.zip",
    "buses_m": "https://rrgtfsfeeds.s3.amazonaws.com/gtfs_m.zip",
    "buses_q": "https://rrgtfsfeeds.s3.amazonaws.com/gtfs_q.zip",
    "buses_si": "https://rrgtfsfeeds.s3.amazonaws.com/gtfs_si.zip",
    "buses_busco": "https://rrgtfsfeeds.s3.amazonaws.com/gtfs_busco.zip",
}


def request_data(url: str) -> zipfile.ZipFile:
    """Request the metadata zip file from the MTA."""
    res = requests.get(url)
    res.raise_for_status()
    return zipfile.ZipFile(io.BytesIO(res.content))


def get_stops(include_buses: bool) -> Generator[dict[str, str], None, None]:
    for source, url in DATA_URLS.items():
        zpfile = request_data(url)
        stops_txt = io.StringIO(zpfile.read("stops.txt").decode())

        def add_source(row: dict[str, str]) -> dict[str, str]:
            return {"_source": source, **row}  # noqa: B023

        yield from map(add_source, csv.DictReader(stops_txt))

        if not include_buses:
            break


@click.command()
@click.argument("query", required=True, nargs=-1, type=str)
@click.option(
    "--json",
    "output_json",
    is_flag=True,
    help="Option to output the data as JSON. Otherwise will be human readable table.",
)
@click.option(
    "--buses",
    "include_buses",
    is_flag=True,
    help="Option to also search bus stops. Slower.",
)
def main(query, output_json, include_buses):
    """Find your stop ID.

    Query a location and look for your stop ID, like:

    $ underground findstops parkside av
    """
    query_str = " ".join(query).lower().strip()  # make into single string

    all_stops = get_stops(include_buses)

    matched_stops = []
    # iterate using dictreader
    for stop in all_stops:
        # skip stations, i only want stop info.
        if stop.get("location_type") == "1":
            continue

        # parse stop direction
        if stop["_source"] != "subway":
            direction = "(BUS)"
        elif stop["stop_id"].endswith("N"):
            direction = "NORTH"
        elif stop["stop_id"].endswith("S"):
            direction = "SOUTH"
        else:
            raise ValueError(f"Cannot parse direction: {stop['stop_id']}.")

        stop["direction"] = direction

        # add if match
        if query_str in stop["stop_name"].lower():
            matched_stops.append(
                dict(
                    stop_id=stop["stop_id"],
                    stop_name=stop["stop_name"].upper(),
                    direction=stop["direction"].upper(),
                    stop_lat=float(stop["stop_lat"]),
                    stop_lon=float(stop["stop_lon"]),
                    source=stop["_source"],
                )
            )

    if not output_json:
        for stop in matched_stops:
            click.echo(
                f"""ID: {stop["stop_id"]:<6}   """
                f"""Direction: {stop["direction"]}    """
                + (f"""Data Source: {stop["source"]:<12} """ if include_buses else "")
                + f"""Lat/Lon: {stop["stop_lat"]:<9},{stop["stop_lon"]:<10}  """
                f"""Name: {stop["stop_name"]}    """
            )
    else:
        click.echo(json.dumps(matched_stops))


if __name__ == "__main__":
    main()
