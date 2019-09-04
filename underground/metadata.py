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
    "W": 16,
    "Z": 36,
}


VALID_ROUTES = set(ROUTE_FEED_MAP.keys())
VALID_FEED_IDS = set(ROUTE_FEED_MAP.values())
