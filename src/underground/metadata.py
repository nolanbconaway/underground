"""Module metadata."""

# because its for the NYC subway
DEFAULT_TIMEZONE = "America/New_York"

# all buses share the same feed url
BUS_URL = "https://gtfsrt.prod.obanyc.com/tripUpdates"

# map a tuple of all routes per
FEED_GROUPS = {
    "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs": (
        "1",
        "2",
        "3",
        "4",
        "5",
        "6",
        "GS",
        "7",
        # Some unusual routes that i have seen in the wild
        "SS",
        "5X",
        "6X",
        "7X",
    ),
    "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-ace": (
        "A",
        "C",
        "E",
        "H",
    ),
    "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-bdfm": (
        "B",
        "D",
        "F",
        "M",
        "FS",
        "FX",  # seen this in the wild as well
    ),
    "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-g": ("G",),
    "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-jz": ("J", "Z"),
    "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-l": ("L",),
    "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-nqrw": (
        "N",
        "R",
        "Q",
        "W",
    ),
    "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-si": ("SI",),
}

# get a route to feed mapping
ROUTE_FEED_MAP = {route: url for url, routes in FEED_GROUPS.items() for route in routes}


VALID_ROUTES = set(ROUTE_FEED_MAP.keys())
VALID_FEED_URLS = set(ROUTE_FEED_MAP.values())


class UnknownRouteOrURL(Exception):
    """Thrown when an unknown route or URL is provided."""


def resolve_url(route_or_url: str) -> str:
    """Return the correct URL, given an unknown route ID or a url."""
    if route_or_url in VALID_FEED_URLS:
        return route_or_url

    if route_or_url == BUS_URL:
        return route_or_url

    if route_or_url == "BUS":
        return BUS_URL

    if route_or_url not in ROUTE_FEED_MAP:
        raise UnknownRouteOrURL(f"Unknown route or url: {route_or_url}")

    return ROUTE_FEED_MAP[route_or_url]
