"""Interact with the MTA GTFS api."""

import os
import time
import typing

import google
import requests
from google.transit import gtfs_realtime_pb2
from protobuf_to_dict import protobuf_to_dict

from underground import metadata


class EmtyFeedError(Exception):
    """Thrown when the GTFS data is empty."""


def load_protobuf(protobuf_bytes: bytes) -> dict:
    """Process a protobuf bytes object into native python.
    
    Parameters
    ----------
    protobuf_bytes : bytes
        Protobuuf data, as returned from the raw request.
    
    Returns
    -------
    Processed feed data.

    """
    feed = gtfs_realtime_pb2.FeedMessage()
    feed.ParseFromString(protobuf_bytes)
    feed_dict = protobuf_to_dict(feed)

    if not feed_dict or "entity" not in feed_dict:
        raise EmtyFeedError

    return feed_dict


def request(
    feed_id: int, retries: int = 100, api_key: str = None, process_response: bool = True
) -> typing.Union[bytes, dict]:
    """Send a get request for realtime feed data, handle retries on error.
    
    Parameters
    ----------
    feed_id : int
        Integer feed ID, per ``https://datamine.mta.info/list-of-feeds``.
    retries : int
        Number of retry attempts, with 1 second timeout between attempts.
        Set to -1 for unlimited. Default 100. 
    api_key : str
       MTA API key. If not provided, it will be read from the $MTA_API_KEY env 
       variable.
    process_response : bool
        Option to process the response into python objects. If true, this function 
        processes the data into native python objects. If false this function returns 
        protobuf bytes. Default True.

    Returns
    -------
    dict
        Dictionary of the current GTFS data.

    """
    # check feed
    if feed_id not in metadata.VALID_FEED_IDS:
        raise ValueError(
            "Invalid feed ID. Must be in `%s`." % str(metadata.VALID_FEED_IDS)
        )

    # get the API key.
    api_key = api_key or os.getenv("MTA_API_KEY", None)
    if api_key is None:
        raise ValueError(
            "No API key. pass to the called function "
            "or set the $MTA_API_KEY environment variable."
        )

    # request in recursive try except to capture occasional MTA file issues.
    try:
        res = requests.get(
            "http://datamine.mta.info/mta_esi.php",
            params=dict(key=api_key, feed_id=feed_id),
        )

        if process_response:
            return load_protobuf(res.content)

        return res.content

    except (EmtyFeedError, google.protobuf.message.DecodeError):
        time.sleep(1)
        return request(
            feed_id=feed_id,
            retries=retries - 1,
            api_key=api_key,
            process_response=process_response,
        )
