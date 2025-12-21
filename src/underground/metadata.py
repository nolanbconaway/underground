"""Module metadata."""

# because its for the NYC subway
DEFAULT_TIMEZONE = "America/New_York"

# map a tuple of all routes per
# fmt: off
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
        # SS route is undocumented but i have seen it here "in the wild".
        "SS",
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
    # buses all share the same feed
    "https://gtfsrt.prod.obanyc.com/tripUpdates": (
        "B1", "B100", "B101", "B103", "B106", "B11", "B111", "B12", "B13", "B14", "B15",
        "B16", "B17", "B2", "B20", "B24", "B25", "B26", "B3", "B31", "B32", "B35",
        "B36", "B37", "B38", "B39", "B4", "B41", "B42", "B43", "B44", "B44+", "B45",
        "B46", "B46+", "B47", "B48", "B49", "B52", "B54", "B57", "B6", "B60", "B61",
        "B62", "B63", "B64", "B65", "B67", "B68", "B69", "B7", "B70", "B74", "B8",
        "B82", "B82+", "B83", "B84", "B9", "B90", "B93", "B94", "B96", "B98", "B99",
        "BM1", "BM2", "BM3", "BM4", "BM5", "BX1", "BX10", "BX11", "BX12", "BX12+",
        "BX13", "BX15", "BX16", "BX17", "BX18A", "BX18B", "BX19", "BX2", "BX20", "BX21",
        "BX22", "BX23", "BX24", "BX25", "BX26", "BX27", "BX28", "BX29", "BX3", "BX30",
        "BX31", "BX32", "BX33", "BX34", "BX35", "BX36", "BX38", "BX39", "BX4", "BX40",
        "BX41", "BX41+", "BX42", "BX46", "BX4A", "BX5", "BX6", "BX6+", "BX7", "BX8",
        "BX9", "BX90", "BX92", "BX95", "BXM1", "BXM10", "BXM11", "BXM18", "BXM2",
        "BXM3", "BXM4", "BXM6", "BXM7", "BXM8", "BXM9", "D90", "D99", "F1", "J90",
        "J99", "L0202", "L0719", "L1227", "L90", "L91", "L92", "M1", "M10", "M100",
        "M101", "M102", "M103", "M104", "M106", "M11", "M116", "M12", "M125", "M14A+",
        "M14D+", "M15", "M15+", "M191", "M2", "M20", "M21", "M22", "M23+", "M3", "M31",
        "M34+", "M34A+", "M35", "M4", "M42", "M5", "M50", "M55", "M57", "M60+", "M66",
        "M7", "M72", "M79+", "M8", "M86+", "M9", "M90", "M96", "M98", "Q06", "Q07",
        "Q08", "Q09", "Q1", "Q10", "Q100", "Q101", "Q102", "Q103", "Q104", "Q107",
        "Q108", "Q11", "Q110", "Q111", "Q112", "Q113", "Q114", "Q115", "Q12", "Q13",
        "Q14", "Q15", "Q16", "Q17", "Q18", "Q19", "Q2", "Q20", "Q22", "Q23", "Q24",
        "Q25", "Q26", "Q27", "Q28", "Q29", "Q3", "Q30", "Q31", "Q32", "Q33", "Q35",
        "Q36", "Q37", "Q38", "Q39", "Q4", "Q40", "Q41", "Q42", "Q43", "Q44+", "Q45",
        "Q46", "Q47", "Q48", "Q49", "Q5", "Q50", "Q51", "Q52+", "Q53+", "Q54", "Q55",
        "Q56", "Q58", "Q59", "Q60", "Q61", "Q63", "Q64", "Q65", "Q66", "Q67", "Q69",
        "Q70+", "Q72", "Q74", "Q75", "Q76", "Q77", "Q80", "Q82", "Q83", "Q84", "Q85",
        "Q86", "Q87", "Q88", "Q89", "Q90", "Q92", "Q93", "Q96", "Q98", "QM1", "QM10",
        "QM11", "QM12", "QM15", "QM16", "QM17", "QM18", "QM2", "QM20", "QM21", "QM24",
        "QM25", "QM31", "QM32", "QM34", "QM35", "QM36", "QM4", "QM40", "QM42", "QM44",
        "QM5", "QM6", "QM63", "QM64", "QM65", "QM68", "QM7", "QM8", "S40", "S42", "S44",
        "S46", "S48", "S51", "S52", "S53", "S54", "S55", "S56", "S57", "S59", "S61",
        "S62", "S66", "S74", "S76", "S78", "S79+", "S81", "S84", "S86", "S89", "S90",
        "S91", "S92", "S93", "S94", "S96", "S96B1", "S96B2", "S96B3", "S98", "SIM1",
        "SIM10", "SIM11", "SIM15", "SIM1C", "SIM2", "SIM22", "SIM23", "SIM24", "SIM25",
        "SIM26", "SIM3", "SIM30", "SIM31", "SIM32", "SIM33", "SIM33C", "SIM34", "SIM35",
        "SIM3C", "SIM4", "SIM4C", "SIM4X", "SIM5", "SIM6", "SIM7", "SIM8", "SIM8X",
        "SIM9", "X27", "X28", "X37", "X38" )
}
# fmt: on

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
        raise ValueError(f"Unknown route or url: {route_or_url}")

    return ROUTE_FEED_MAP[ROUTE_REMAP[route_or_url]]
