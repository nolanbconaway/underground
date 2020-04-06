"""Get upcoming stops along a train route."""

import csv
import io
import json
import zipfile

import click
import requests

# url to the zip file containing MTA metadata
DATA_URL = "http://web.mta.info/developers/data/nyct/subway/google_transit.zip"


def request_data() -> zipfile.ZipFile:
    """Request the metadata zip file from the MTA."""
    res = requests.get(DATA_URL)
    res.raise_for_status()
    return zipfile.ZipFile(io.BytesIO(res.content))


@click.command()
@click.argument("query", required=True, nargs=-1, type=str)
@click.option(
    "--json",
    "output_json",
    is_flag=True,
    help="Option to output the data as JSON. Otherwise will be human readable table.",
)
def main(query, output_json):
    """Find your stop ID.
    
    Query a location and look for your stop ID, like:
    
    $ underground findstops parkside av
    """
    query_str = " ".join(query).lower().strip()  # make into single string

    # get zip file
    zpfile = request_data()
    stops_txt = io.StringIO(zpfile.read("stops.txt").decode())

    matched_stops = []
    # iterate using dictreader
    for stop in csv.DictReader(stops_txt):
        # skip stations, i only want stop info.
        if stop["location_type"] == "1":
            continue

        # parse stop direction
        if stop["stop_id"].endswith("N"):
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
                )
            )

    if not output_json:
        for stop in matched_stops:
            click.echo(
                f"""ID: {stop['stop_id']}    """
                f"""Direction: {stop['direction']}    """
                f"""Lat/Lon: {stop['stop_lat']},{stop['stop_lon']}    """
                f"""Name: {stop['stop_name']}"""
            )
    else:
        click.echo(json.dumps(matched_stops))


if __name__ == "__main__":
    main()
