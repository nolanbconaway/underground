"""Save feed data."""

import json

import click

from underground import feed, metadata


@click.command()
@click.argument("route_or_url")
@click.option(
    "--api-key",
    "api_key",
    default=None,
    help="MTA API key. Will be read from $MTA_API_KEY if not provided.",
)
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
def main(route_or_url, api_key, output_json, retries):
    """Request an MTA feed via a route or URL.

    ROUTE_OR_URL may be either a feed URL or a route (which will be used to look up
    the feed url).

    Examples (both access the same feed):

      \b
      underground feed Q --json > feed_nrqw.json
  
      \b
      URL='https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-nqrw' &&
      underground feed $URL --json > feed_nrqw.json
    """
    if route_or_url not in metadata.VALID_ROUTES.union(metadata.VALID_FEED_URLS):
        raise click.ClickException(
            f"Invalid route or URL. Try a route like {metadata.VALID_ROUTES} "
            "or a url from https://api.mta.info/#/subwayRealTimeFeeds."
        )

    data = feed.request_robust(
        route_or_url=route_or_url,
        retries=retries,
        api_key=api_key,
        return_dict=output_json,
    )

    if output_json:
        click.echo(json.dumps(data))
    else:
        click.echo(data, nl=False)


if __name__ == "__main__":
    main()
