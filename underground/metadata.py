"""Module metadata."""

ROUTE_FEED_MAP = {
    "1": 1,
    "2": 1,
    "3": 1,
    "4": 1,
    "5": 1,
    "6": 1,
    "7": 51,
    "A": 26,
    "B": 21,
    "C": 26,
    "D": 21,
    "E": 26,
    "F": 21,
    "FS": 26,
    "G": 31,
    "GS": 1,
    "H": 26,
    "J": 36,
    "L": 2,
    "M": 21,
    "N": 16,
    "Q": 16,
    "R": 16,
    "SI": 11,
    "SS": 51,  # There is no documentation on this route but it has appeared here.
    "W": 16,
    "Z": 36,
}

# There are some routes with aliases that we need to map onto the original ID.
# The empty string occurs if the trip has not yet been assigned a route. I have found
# these cases "in the wild" and would rather write code to skip over them than have
# the application break.
ROUTE_REMAP = {"5X": "5", "6X": "6", "7X": "7", "FX": "F", "": ""}
for k in ROUTE_FEED_MAP:
    ROUTE_REMAP[k] = k


def get_feed_id(route_id: str) -> int:
    """Return the feed ID for a given route."""
    return ROUTE_FEED_MAP[ROUTE_REMAP[route_id]]


VALID_FEED_IDS = set(ROUTE_FEED_MAP.values())
