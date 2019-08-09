"""Interact with the MTA GTFS api."""

import time

import google
import requests

from underground import metadata
from underground.models import GTFSEmptyError, SubwayFeed


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
        feed_data = SubwayFeed.from_content(res.content)

    except (GTFSEmptyError, google.protobuf.message.DecodeError):
        if retries == 0:
            raise

        time.sleep(1)
        return request_feed_data(api_key, feed_id, retries - 1)

    return feed_data


def get_stops(api_key: str, feed_id: int, retries: int = 100) -> dict:
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
    mta_data = request_feed_data(api_key=api_key, feed_id=feed_id, retries=retries)
    return mta_data.extract_stop_dict()
