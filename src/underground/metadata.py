"""Module metadata."""

# because its for the NYC subway
DEFAULT_TIMEZONE = "US/Eastern"

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
    ),
    # SS route is undocumented but i have seen it here "in the wild".
    "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-7": (
        "7",
        "SS",
    ),
    "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-ace": (
        "A",
        "C",
        "E",
        "FS",
        "H",
    ),
    "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-bdfm": (
        "B",
        "D",
        "F",
        "M",
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

# There are some routes with aliases that we need to map onto the original ID.
# The empty string occurs if the trip has not yet been assigned a route. I have found
# these cases "in the wild" and would rather write code to skip over them than have
# the application break.
ROUTE_REMAP = {"5X": "5", "6X": "6", "7X": "7", "FX": "F", "": ""}
for k in ROUTE_FEED_MAP:
    ROUTE_REMAP[k] = k

VALID_ROUTES = set(ROUTE_FEED_MAP.keys())
VALID_FEED_URLS = set(ROUTE_FEED_MAP.values())


def resolve_url(route_or_url: str) -> str:
    """Return the correct URL, given an unknown route ID or a url."""
    if route_or_url in VALID_FEED_URLS:
        return route_or_url

    if route_or_url not in ROUTE_REMAP:
        raise ValueError("Unknown route or url: %s" % route_or_url)

    return ROUTE_FEED_MAP[ROUTE_REMAP[route_or_url]]
