"""Pydantic data models for MTA GFTS data."""

import datetime
import typing
import zoneinfo

import pydantic

from underground import feed, metadata


class UnixTimestamp(pydantic.BaseModel):
    """A unix timestamp model."""

    time: typing.Optional[datetime.datetime] = None

    @property
    def timestamp_nyc(self) -> typing.Optional[datetime.datetime]:
        """Return the NYC datetime."""
        if not self.time:
            return None
        return self.time.astimezone(zoneinfo.ZoneInfo(metadata.DEFAULT_TIMEZONE))


class FeedHeader(pydantic.BaseModel):
    """Data model for the feed header."""

    gtfs_realtime_version: str
    timestamp: datetime.datetime

    @property
    def timestamp_nyc(self) -> datetime.datetime:
        """Return the NYC datetime of the header."""
        return self.timestamp.astimezone(zoneinfo.ZoneInfo(metadata.DEFAULT_TIMEZONE))


class Trip(pydantic.BaseModel):
    """Model describing a train trip."""

    trip_id: str
    start_time: typing.Optional[datetime.time] = None
    start_date: int
    route_id: str

    @pydantic.field_validator("start_date")
    def check_start_date(cls, start_date):
        """Start_date is an int, so check it conforms to date expectations."""
        if start_date < 19000101:
            raise ValueError("Probably not a date.")

        return start_date

    @pydantic.field_validator("route_id")
    def check_route(cls, route_id):
        """Check for a valid route ID value."""
        if route_id not in metadata.ROUTE_REMAP:
            raise ValueError(
                f"Invalid route ({route_id}). Must be one of {set(metadata.ROUTE_REMAP.keys())}."
            )

        return route_id

    @property
    def route_id_mapped(self) -> str:
        """Find the parent route ID.

        This is helpful for grabbing the, e.g., 5 Train when you might have a 5X.
        """
        return metadata.ROUTE_REMAP[self.route_id]

    @property
    def route_is_assigned(self) -> bool:
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
    arrival: typing.Optional[UnixTimestamp] = None
    departure: typing.Optional[UnixTimestamp] = None

    @property
    def depart_or_arrive(self) -> typing.Optional[UnixTimestamp]:
        """Return the departure or arrival time if either are specified.

        This OR should usually be called because the MTA is inconsistent about when
        arrival/departure are specified, but when both are supplied they are usually
        the same time.
        """
        if self.departure is not None and self.departure.time is not None:
            return self.departure
        elif self.arrival is not None and self.arrival.time is not None:
            return self.arrival


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
    stop_time_update: typing.Optional[list[StopTimeUpdate]] = None


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
    timestamp: typing.Optional[datetime.datetime] = None
    current_stop_sequence: typing.Optional[int] = None
    stop_id: typing.Optional[str] = None


class Entity(pydantic.BaseModel):
    """Model for an element within feed entity.

    As a side note, I have never found a case where there is BOTH a VehiclePosition and
    a TripUpdate.
    """

    id: str
    vehicle: typing.Optional[Vehicle] = None
    trip_update: typing.Optional[TripUpdate] = None


class SubwayFeed(pydantic.BaseModel):
    """Model for the main MTA feed data structure.

    Includes methods for easy creation and parsing of data.
    """

    header: FeedHeader
    entity: list[Entity]

    @classmethod
    def get(cls, route_or_url: str, retries: int = 100) -> "SubwayFeed":
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

        Returns
        -------
        SubwayFeed
            An instance of the SubwayFeed class with the requested data.

        """
        return cls(
            **feed.request_robust(route_or_url=route_or_url, retries=retries, return_dict=True)
        )

    def extract_stop_dict(
        self, timezone: str = metadata.DEFAULT_TIMEZONE, stalled_timeout: int = 90
    ) -> dict[str, dict[str, list[datetime.datetime]]]:
        """Get the departure times for all stops in the feed.

        Parameters
        ----------
        timezone : str
            Name of the timezone to return within. Default to NYC time.
        stalled_timeout : int
            Number of seconds between the last movement of a train and the API update before
            considering a train stalled. Default is 90 as recommended by the MTA.
            Numbers less than 1 disable this check.

        Returns
        -------
        dict
            Dictionary containing train departure for all stops in the gtfs data.
            The dictionary will be a schema like ``{route: {stop: [t1, t2]}}``.

        """

        trip_updates = (x.trip_update for x in self.entity if x.trip_update is not None)
        vehicles = {e.vehicle.trip.trip_id: e.vehicle for e in self.entity if e.vehicle is not None}

        def is_trip_active(update: TripUpdate) -> bool:
            has_route = update.trip.route_is_assigned
            has_stops = update.stop_time_update is not None

            vehicle = vehicles.get(update.trip.trip_id)
            if stalled_timeout < 1 or vehicle is None or vehicle.timestamp is None:
                return has_route and has_stops

            # as recommended by the MTA, we use these timestamps to determine if a train is stalled
            train_stalled = (self.header.timestamp - vehicle.timestamp) > datetime.timedelta(
                seconds=stalled_timeout
            )
            return has_route and has_stops and not train_stalled

        # grab the updates with routes and stop times
        trip_updates_with_stops = filter(is_trip_active, trip_updates)
        # create (route, stop, time) tuples from each trip
        stops_flat = (
            (
                trip.trip.route_id_mapped,
                stop.stop_id,
                (stop.depart_or_arrive).time.astimezone(zoneinfo.ZoneInfo(timezone)),
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
