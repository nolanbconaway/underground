"""Pydantic data models for MTA GFTS data."""

import datetime
import typing
from operator import attrgetter

import pydantic
import pytz

from underground import feed, metadata


class UnixTimestamp(pydantic.BaseModel):
    """A unix timestamp model."""

    time: datetime.datetime

    @property
    def timestamp_nyc(self):
        """Return the NYC datetime."""
        return self.time.astimezone(pytz.timezone(metadata.DEFAULT_TIMEZONE))


class FeedHeader(pydantic.BaseModel):
    """Data model for the feed header."""

    gtfs_realtime_version: str
    timestamp: datetime.datetime

    @property
    def timestamp_nyc(self):
        """Return the NYC datetime of the header."""
        return self.timestamp.astimezone(pytz.timezone(metadata.DEFAULT_TIMEZONE))


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
        """Check for a valid route ID value."""
        if route_id not in metadata.ROUTE_REMAP:
            raise ValueError(
                "Invalid route (%s). Must be one of %s."
                % (route_id, str(set(metadata.ROUTE_REMAP.keys())))
            )

        return route_id

    @property
    def route_id_mapped(self):
        """Find the parent route ID.
        
        This is helpful for grabbing the, e.g., 5 Train when you might have a 5X.
        """
        return metadata.ROUTE_REMAP[self.route_id]

    @property
    def route_is_assigned(self):
        """Return a flag indicating that there is a route."""
        return self.route_id != ""


class StopTimeUpdate(pydantic.BaseModel):
    """Stop times for a trip.

    This includes all future Stop Times for the trip but Stop Times from the past
    are omitted. The first StopTime in the sequence is the stop the train is
    currently approaching, stopped at or about to leave. A stop is dropped from
    the sequence when the train departs the station.

    Transit times are provided at all in-between stops except at those locations where 
    there are “scheduled holds”. At those locations both arrival and departure times 
    are given.

    Note that the predicted times are not updated when the train is not moving. Feed 
    consumers can detect this condition using the timestamp in the VehiclePosition 
    message.
    """

    stop_id: str
    arrival: UnixTimestamp = None
    departure: UnixTimestamp = None

    @property
    def depart_or_arrive(self) -> UnixTimestamp:
        """Return the departure or arrival time if either are specified.
        
        This OR should usually be called because the MTA is inconsistent about when
        arrival/departure are specified, but when both are supplied they are usually
        the same time.
        """
        return self.departure or self.arrival


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
    """Data model for the vehicle feed message.
    
    From the MTA docs:
    
    A VehiclePosition entity is provided for every trip when it starts moving. Note that 
    a train can be assigned (see TripUpdate) but has not started to move (e.g. a train 
    waiting to leave the origin station), therefore, no VehiclePosition is provided.

    The motivation to include VehiclePosition is to provide the timestamp field. This 
    is the time of the last detected movement of the train. This allows feed consumers 
    to detect the situation when a train stops moving (aka stalled). The platform 
    countdown clocks only count down when trains are moving otherwise they persist the 
    last published arrival time for that train. If one wants to mimic this behavior you 
    must first determine the absence of movement (stalled train condition) ), then the
    countdown must be stopped.

    As an example, a countdown could be stopped for a trip when the difference between 
    the timestamp in the VehiclePosition and the timestamp in the field header is 
    greater than, 90 seconds.
    
    Note: since VehiclePosition information is not provided until the train starts 
    moving, it is recommended that feed consumers use the origin terminal departure to 
    determine a train stalled condition. 
    """

    trip: Trip
    timestamp: datetime.datetime = None
    current_stop_sequence: int = None
    stop_id: str = None


class Entity(pydantic.BaseModel):
    """Model for an element within feed entity.
    
    As a side note, I have never found a case where there is BOTH a VehiclePosition and
    a TripUpdate.
    """

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
    def get(route_or_url: str, retries: int = 100, api_key: str = None) -> "SubwayFeed":
        """Request feed data from the MTA.
        
        Parameters
        ----------
        route_or_url : str
            Route ID or feed url (per ``https://api.mta.info/#/subwayRealTimeFeeds``). 
            If a route, the URL for that route is looked up. All routes served by that 
            URL will be included in the result.
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
                route_or_url=route_or_url,
                retries=retries,
                api_key=api_key,
                return_dict=True,
            )
        )

    def extract_stop_dict(self, timezone: str = metadata.DEFAULT_TIMEZONE) -> dict:
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

        # grab the updates with routes and stop times
        trip_updates_with_stops = filter(
            lambda x: x.trip.route_is_assigned and x.stop_time_update is not None,
            trip_updates,
        )
        # create (route, stop, time) tuples from each trip
        stops_flat = (
            (
                trip.trip.route_id_mapped,
                stop.stop_id,
                (stop.depart_or_arrive).time.astimezone(pytz.timezone(timezone)),
            )
            for trip in trip_updates_with_stops
            for stop in trip.stop_time_update
            if stop.depart_or_arrive is not None
            and stop.depart_or_arrive.time >= self.header.timestamp
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
