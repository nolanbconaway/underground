"""Interact with the MTA GTFS api."""

import os
import time
import typing

import google
import protobuf_to_dict
import requests
from google.transit import gtfs_realtime_pb2

from underground import metadata


class EmptyFeedError(Exception):
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
    feed_dict = protobuf_to_dict.protobuf_to_dict(feed)
    if not feed_dict or "entity" not in feed_dict:
        raise EmptyFeedError

    return feed_dict


def request(feed_id: int, api_key: str = None) -> bytes:
    """Send a HTTP GET request to the MTA for realtime feed data.

    Occassionally a feed is requested as the MTA is writing updated data to the file,
    and the feed's contents are not complete. This function does _not_ validate the 
    contents of the data, but only returns the request contents as served by the MTA.
    
    Parameters
    ----------
    feed_id : int
        Integer feed ID, per ``https://datamine.mta.info/list-of-feeds``.
    api_key : str
       MTA API key. If not provided, it will be read from the $MTA_API_KEY env 
       variable.

    Returns
    -------
    bytes
        Protobuf data.

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

    # make the request
    res = requests.get(
        "http://datamine.mta.info/mta_esi.php",
        params=dict(key=api_key, feed_id=feed_id),
    )
    res.raise_for_status()

    return res.content


def request_robust(
    feed_id: int, retries: int = 100, api_key: str = None, return_dict: bool = False
) -> typing.Union[dict, bytes]:
    """Request feed data with validations and retries.

    Occassionally a feed is requested as the MTA is writing updated data to the file,
    and the feed's contents are not complete. This function validates data completeness 
    and retries if the data are not complete. Since we are processing the protobuf 
    anyway, there is an option to return the processed data as familiar python objects.
    
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
    return_dict : bool
        Option to return the process data as a dict rather than as raw protobuf data.
        This is equivalent to running ``load_protobuf(request_robust(...))``.
    
    Returns
    -------
    bytes or dict
        The current GTFS data as bytes or a dictionary, depending on the 
        ``return_dict`` flag.

    """
    # get protobuf bytes
    protobuf_data = request(feed_id=feed_id, api_key=api_key)
    for attempt in range(retries + 1):
        try:
            feed_dict = load_protobuf(protobuf_data)
            break  # break if success

        except (EmptyFeedError, google.protobuf.message.DecodeError):

            # raise if we're out of retries
            if attempt == retries:
                raise

            # wait 1 second and then make new protobuf data
            time.sleep(1)  # be cool to the MTA
            protobuf_data = request(feed_id=feed_id, api_key=api_key)

    return feed_dict if return_dict else protobuf_data
