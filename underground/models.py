"""Pydantic data models for MTA GFTS data."""

import datetime
import typing
from operator import attrgetter

import pydantic
import pytz

from underground import dateutils, feed, metadata


class UnixTimestamp(pydantic.BaseModel):
    """A unix timestamp model."""

    time: datetime.datetime

    @property
    def timestamp_nyc(self):
        """Return the NYC datetime."""
        return self.time.astimezone(pytz.timezone(dateutils.DEFAULT_TIMEZONE))


class FeedHeader(pydantic.BaseModel):
    """Data model for the feed header."""

    gtfs_realtime_version: str
    timestamp: datetime.datetime

    @property
    def timestamp_nyc(self):
        """Return the NYC datetime of the header."""
        return self.timestamp.astimezone(pytz.timezone(dateutils.DEFAULT_TIMEZONE))


class Trip(pydantic.BaseModel):
    """Model describing a train trip."""

    trip_id: str
    start_time: datetime.time = None
    start_date: int
    route_id: str

    @pydantic.validator("start_date")
    def check_start_date(cls, start_date):
        """Start_date is an int, so check it conforms to date expectations."""
        if start_date < 19000101:
            raise ValueError("Probably not a date.")

        return start_date

    @pydantic.validator("route_id")
    def check_route(cls, route_id):
        """Start_date is an int, so check it conforms to date expectations."""
        if route_id not in metadata.ROUTE_REMAP:
            raise ValueError(
                "Invalid route (%s). Must be one of %s."
                % (route_id, str(set(metadata.ROUTE_REMAP.keys())))
            )

        return route_id

    @property
    def route_id_mapped(self):
        """Run some transformations on self."""
        return metadata.ROUTE_REMAP[self.route_id]


class StopTimeUpdate(pydantic.BaseModel):
    """Stop times for a trip.

    This includes all future Stop Times for the trip but StopTimes from the past
    are omitted. The first StopTime in the sequence is the stop the train is
    currently approaching, stopped at or about to leave. A stop is dropped from
    the sequence when the train departs the station.
    """

    stop_id: str
    arrival: UnixTimestamp = None
    departure: UnixTimestamp = None


class TripUpdate(pydantic.BaseModel):
    """Info on trips that are underway or scheduled to start within 30 mins.

    Trips are usually assigned to a physical train a few minutes before the scheduled 
    start time, sometimes just a few seconds before.

    If a trip is included in the GTFS-realtime feed, there is a high probability that 
    it will depart from its originating terminal as planned. It is more likely that a 
    train that is never assigned a trip identifier to be changed or cancelled than an 
    assigned one.
    """

    trip: Trip
    stop_time_update: typing.List[StopTimeUpdate] = None


class Vehicle(pydantic.BaseModel):
    """Data model for the vehicle feed message."""

    trip: Trip
    timestamp: datetime.datetime = None
    current_stop_sequence: int = None
    stop_id: str = None


class Entity(pydantic.BaseModel):
    """Model for an element within feed entity."""

    id: str
    vehicle: Vehicle = None
    trip_update: TripUpdate = None


class SubwayFeed(pydantic.BaseModel):
    """Model for the main MTA feed data structure.
    
    Includes methods for easy creation and parsing of data.
    """

    header: FeedHeader
    entity: typing.List[Entity]

    @staticmethod
    def get(feed_id: int, retries: int = 100, api_key: str = None) -> "SubwayFeed":
        """Request feed data from the MTA.
        
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

        Returns
        -------
        SubwayFeed
            An instance of the SubwayFeed class with the requested data.
        
        """
        return SubwayFeed(
            **feed.request_robust(
                feed_id=feed_id, retries=retries, api_key=api_key, return_dict=True
            )
        )

    def extract_stop_dict(self, timezone: str = dateutils.DEFAULT_TIMEZONE) -> dict:
        """Get the departure times for all stops in the feed.

        Parameters
        ----------
        timezone : str
            Name of the timezone to return within. Default to NYC time.

        Returns
        -------
        dict
            Dictionary containing train departure for all stops in the gtfs data.
            The dictionary will be a schema like ``{route: {stop: [t1, t2]}}``.
        
        """
        # filter down data to trips with an update
        entities_with_updates = filter(lambda x: x.trip_update is not None, self.entity)
        trip_updates = map(attrgetter("trip_update"), entities_with_updates)

        # grab the updates with stop times
        trip_updates_with_stops = filter(
            lambda x: x.stop_time_update is not None, trip_updates
        )
        # create (route, stop, time) tuples from each trip
        stops_flat = (
            (
                trip.trip.route_id_mapped,
                stop.stop_id,
                (stop.departure or stop.arrival).time.astimezone(
                    pytz.timezone(timezone)
                ),
            )
            for trip in trip_updates_with_stops
            for stop in trip.stop_time_update
            if stop.departure is not None or stop.arrival is not None
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
