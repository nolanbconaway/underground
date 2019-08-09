"""Datetime utilities for the module."""

import datetime
import typing

import pytz

# because its for the NYC subway
DEFAULT_TIMEZONE = "US/Eastern"


def current_time(
    timezone: str = DEFAULT_TIMEZONE, epoch: bool = False
) -> typing.Union[datetime.datetime, int]:
    """Get the current datetime in the timezone.
    
    Optionally, get the epoch time via epoch=True.
        
    Parameters
    ----------
    timezone : str
       Name of the timezone to get time within. Defaults to US/Eastern.
    epoch : bool
        Option to get a unix timestamp .

    Returns
    -------
    int or datetime
        Current time.

    """
    # timezone aware utc time
    utcnow = datetime.datetime.now(pytz.timezone("UTC"))

    if epoch:
        return int(utcnow.timestamp())

    return utcnow.astimezone(pytz.timezone(timezone))


def epoch_to_datetime(
    epoch: int, timezone: str = DEFAULT_TIMEZONE
) -> datetime.datetime:
    """Convert epoch time into a datetime in the timezone.
    
    Epoch is assumed to be the unix time in UTC.

    Parameters
    ----------
    epoch : int
       Unix timestamp.
    timezone : sre
       Name of the timezone to convert into. Defaults to US/Eastern.

    Returns
    -------
    datetime

    """
    return (
        pytz.timezone("UTC")
        .localize(datetime.datetime.utcfromtimestamp(epoch))
        .astimezone(pytz.timezone(timezone))
    )


def datetime_to_epoch(dttm: datetime.datetime) -> int:
    """Return a unix timestmap from a datetime.
    
    Parameters
    ----------
    dttm : datetime

    Returns
    -------
    int

    """
    return int(dttm.astimezone(pytz.timezone("UTC")).timestamp())


def datetime_to_timestring(dttm: datetime.datetime) -> str:
    """Convert a datetime to a time string reading HH:MM.
    
    Parameters
    ----------
    dttm : datetime

    Returns
    -------
    str
        String formatted time reading HH:MM, in 12-hour time without leading 0s 
        for the hour.

    """
    res = dttm.strftime("%I:%M")
    return res if res[0] != "0" else res[1:]


def epoch_to_timestring(epoch: int) -> str:
    """Convert an epoch stamp to a time string.
    
    Wraps the datetime_to_timestring and epoch_to_datetime functions.

    Parameters
    ----------
    epoch : int

    Returns
    -------
    str
        String formatted time reading HH:MM, in 12-hour time without leading 0s 
        for the hour.

    """
    return datetime_to_timestring(epoch_to_datetime(epoch))
