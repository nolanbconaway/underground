"""Interact with the MTA GTFS api."""

import time
from operator import itemgetter

import google
import requests
from google.transit import gtfs_realtime_pb2
from protobuf_to_dict import protobuf_to_dict

from mta import dateutils, metadata


class GTFSEmptyError(Exception):
    """Thrown when the GTFS data is empty."""


def parse_feed_data(gtfs_data):
    """Parse raw GTFS data into native python objects."""
    feed = gtfs_realtime_pb2.FeedMessage()
    feed.ParseFromString(gtfs_data)
    feed_dict = protobuf_to_dict(feed)

    if not feed_dict or "entity" not in feed_dict:
        raise GTFSEmptyError

    return feed_dict


def request_feed_data(api_key: str, feed_id: int, retries: int = 100) -> dict:
    """Send a get request for realtime feed data, handle retries on error.
    
    Parameters
    ----------
    api_key : str
       MTA API key.
    feed_id : int
        Integer feed ID, per ``https://datamine.mta.info/list-of-feeds``.
    retries : int
        Number of retry attempts, with 1 second timeout between attempts.
        Set to -1 for unlimited. Default 100. 

    Returns
    -------
    dict
        Dictionary of the current GTFS data.

    """
    if feed_id not in metadata.VALID_FEED_IDS:
        raise ValueError(
            "Invalid feed ID. Must be in `%s`." % str(metadata.VALID_FEED_IDS)
        )

    try:
        res = requests.get(
            "http://datamine.mta.info/mta_esi.php",
            params=dict(key=api_key, feed_id=feed_id),
        )
        feed_dict = parse_feed_data(res.content)

    except (GTFSEmptyError, google.protobuf.message.DecodeError):
        if retries == 0:
            raise

        time.sleep(1)
        return request_feed_data(api_key, feed_id, retries - 1)

    return feed_dict


def extract_stop_dict(gtfs_result: dict) -> dict:
    """Get the epoch timestamps of the next trains from a gtfs dict.
    
    Parameters
    ----------
    gtfs_result : dict
        GTFS data, as returned from ``request_feed_data``.

    Returns
    -------
    dict
        Dictionary containing train departure for all stops in the gtfs data.
        The dictionary will be a schema like ``{route: {stop: [t1, t2]}}``.
    
    """
    # filter down data to trips with an update
    updates = filter(lambda x: "trip_update" in x, gtfs_result["entity"])

    # grab the updates with stop times
    updates = map(itemgetter("trip_update"), updates)
    updates = filter(lambda x: "stop_time_update" in x, updates)

    # create (route, stop, time) tuples from each trip
    stops_flat = (
        (
            trip["trip"]["route_id"],
            stop["stop_id"],
            dateutils.epoch_to_datetime(stop["departure"]["time"]),
        )
        for trip in updates
        for stop in trip["stop_time_update"]
    )

    # group into a dict like {route: stop: [t1, t2]}
    stops_grouped = dict()

    for route_id, stop_id, departure in stops_flat:
        if route_id not in stops_grouped:
            stops_grouped[route_id] = dict()

        if stop_id not in stops_grouped[route_id]:
            stops_grouped[route_id][stop_id] = []

        stops_grouped[route_id][stop_id].append(departure)

    return stops_grouped


def get_feed_stops(api_key: str, feed_id: int, retries: int = 100) -> dict:
    """Request feed data and extract train stop times.

    This function combines ``request_feed_data`` and ``extract_stop_dict``
    but does not allow you to save the feed data.
    
    Parameters
    ----------
    api_key : str
       MTA API key.
    feed_id : int
        Integer feed ID, per ``https://datamine.mta.info/list-of-feeds``.
    retries : int
        Number of retry attempts, with 1 second timeout between attempts.
        Set to -1 for unlimited. Default 100. 

    Returns
    -------
    dict
        Dictionary containing train departure for all stops in the gtfs data.
        The dictionary will be a schema like ``{route: {stop: [t1, t2]}}``.

    """
    return extract_stop_dict(
        request_feed_data(api_key=api_key, feed_id=feed_id, retries=retries)
    )
