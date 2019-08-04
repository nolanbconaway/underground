"""Pydantic data models for MTA GFTS data."""

import typing
from operator import attrgetter, itemgetter

import pendulum
import pydantic
from google.transit import gtfs_realtime_pb2
from protobuf_to_dict import protobuf_to_dict

from mta import dateutils, metadata


class GTFSEmptyError(Exception):
    """Thrown when the GTFS data is empty."""


class UnixTimestamp(pydantic.BaseModel):
    """A unix timestamp model."""

    time: pendulum.DateTime

    @property
    def timestamp_nyc(self):
        """Return the NYC datetime."""
        return pendulum.instance(self.time).in_tz(dateutils.DEFAULT_TIMEZONE)


class FeedHeader(pydantic.BaseModel):
    """Data model for the feed header."""

    gtfs_realtime_version: str
    timestamp: pendulum.DateTime

    @property
    def timestamp_nyc(self):
        """Return the NYC datetime of the header."""
        return pendulum.instance(self.timestamp).in_tz(dateutils.DEFAULT_TIMEZONE)


class Trip(pydantic.BaseModel):
    """Model describing a train trip."""

    trip_id: str
    start_time: pendulum.Time
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
        if route_id not in metadata.VALID_ROUTES:
            raise ValueError(
                "Invalid route. Must be one of %s." % str(metadata.VALID_ROUTES)
            )

        return route_id


class StopTimeUpdate(pydantic.BaseModel):
    """Stop times for a trip.

    This includes all future Stop Times for the trip but StopTimes from the past
    are omitted. The first StopTime in the sequence is the stop the train is
    currently approaching, stopped at or about to leave. A stop is dropped from
    the sequence when the train departs the station.
    """

    stop_id: str
    arrival: UnixTimestamp
    departure: UnixTimestamp


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
    timestamp: pendulum.DateTime = None
    current_stop_sequence: int = None
    stop_id: str


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

    @classmethod
    def from_content(cls, gtfs_data):
        """Parse raw GTFS data into a pydantic model."""
        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(gtfs_data)
        feed_dict = protobuf_to_dict(feed)

        if not feed_dict or "entity" not in feed_dict:
            raise GTFSEmptyError

        return cls(**feed_dict)

    def extract_stop_dict(self) -> dict:
        """Get the departure times for all stops in the feed.

        Returns
        -------
        dict
            Dictionary containing train departure for all stops in the gtfs data.
            The dictionary will be a schema like ``{route: {stop: [t1, t2]}}``.
        
        """
        # filter down data to trips with an update
        entities = filter(lambda x: x.trip_update is not None, self.entity)
        entities_with_updates = filter(lambda x: x.trip_update is not None, entities)
        trip_updates = map(attrgetter("trip_update"), entities_with_updates)

        # grab the updates with stop times
        trip_updates_with_stops = filter(
            lambda x: x.stop_time_update is not None, trip_updates
        )
        # create (route, stop, time) tuples from each trip
        stops_flat = (
            (trip.trip.route_id, stop.stop_id, stop.departure.time)
            for trip in trip_updates_with_stops
            for stop in trip.stop_time_update
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
