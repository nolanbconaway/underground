"""Save feed data."""

import json

import click

from underground import feed


@click.command()
@click.argument("route_or_url")
@click.option(
    "--json",
    "output_json",
    is_flag=True,
    help="Option to output the feed data as JSON. Otherwise output will be bytes.",
)
@click.option(
    "-r",
    "--retries",
    "retries",
    default=100,
    type=int,
    help="Retry attempts in case of API connection failure. Default 100.",
)
def main(route_or_url: str, output_json: bool, retries: int):
    """Request an MTA feed via a route or URL.

    ROUTE_OR_URL may be either a feed URL or a route (which will be used to look up
    the feed url). ROUTE_OR_URL may also be "BUS" to access the bus feed.

    Examples (both access the same feed):

      \b
      underground feed Q --json > feed_nrqw.json

      \b
      URL='https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-nqrw' &&
      underground feed $URL --json > feed_nrqw.json
    """
    data = feed.request_robust(route_or_url=route_or_url, retries=retries, return_dict=output_json)
    if output_json:
        click.echo(json.dumps(data))
    else:
        click.echo(data, nl=False)


if __name__ == "__main__":
    main()
