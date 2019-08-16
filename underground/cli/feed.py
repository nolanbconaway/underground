"""Save feed data."""

import json

import click

from underground import feed, metadata


@click.command()
@click.argument("feed_id", type=click.Choice([str(i) for i in metadata.VALID_FEED_IDS]))
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
def main(feed_id, api_key, output_json, retries):
    """Request an MTA feed."""
    data = feed.request_robust(
        feed_id=int(feed_id), retries=retries, api_key=api_key, return_dict=output_json
    )

    if output_json:
        click.echo(json.dumps(data))
    else:
        click.echo(data, nl=False)


if __name__ == "__main__":
    main()
