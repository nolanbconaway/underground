"""Data model tests."""

import datetime
import os

import pytest
import zoneinfo
from requests_mock import ANY as requests_mock_any

from underground import SubwayFeed, models
from underground.feed import load_protobuf
from underground.metadata import DEFAULT_TIMEZONE

from . import DATA_DIR, TEST_PROTOBUFS


def test_unix_timestamp():
    """Test that datetimes are handled correctly."""
    unix_ts = models.UnixTimestamp(time=0)
    epoch_time = datetime.datetime(1970, 1, 1, 0, 0, 0, 0, zoneinfo.ZoneInfo("UTC"))
    assert unix_ts.time == epoch_time
    assert unix_ts.timestamp_nyc == epoch_time.astimezone(zoneinfo.ZoneInfo(DEFAULT_TIMEZONE))


def test_header_nyc_time():
    """Test the nyc time transform for feed header."""
    header = models.FeedHeader(gtfs_realtime_version="1", timestamp=0)
    assert header.timestamp_nyc.minute == 0


def test_trip_invalid_date():
    """Test valuerror for invalid dates."""
    with pytest.raises(ValueError):
        models.Trip(trip_id="1", start_date=0, route_id="5")


def test_trip_invalid_feed():
    """Test valuerror for invalid feeds."""
    with pytest.raises(ValueError):
        models.Trip(trip_id="1", start_date=20190101, route_id="FAKE")


def test_extract_stop_dict():
    """Test that the correct train times are extracted."""
    sample_data = {
        "header": {"gtfs_realtime_version": "1.0", "timestamp": 0},
        "entity": [
            {
                "id": "1",
                "trip_update": {
                    "trip": {"trip_id": "X", "start_date": "20190726", "route_id": "1"},
                    "stop_time_update": [
                        {"arrival": {"time": 0}, "stop_id": "ONE"},
                        {"arrival": {"time": 1}, "stop_id": "TWO"},
                    ],
                },
            },
            {
                "id": "2",
                "trip_update": {
                    "trip": {"trip_id": "X", "start_date": "20190726", "route_id": "1"},
                    "stop_time_update": [{"arrival": {"time": 3}, "stop_id": "TWO"}],
                },
            },
        ],
    }
    stops = SubwayFeed(**sample_data).extract_stop_dict()
    assert len(stops["1"]["ONE"]) == 1
    assert len(stops["1"]["TWO"]) == 2


@pytest.mark.parametrize("filename", TEST_PROTOBUFS)
def test_on_sample_protobufs(filename):
    """Make sure the model can load up one sample from all the feeds."""
    with open(os.path.join(DATA_DIR, filename), "rb") as file:
        data = load_protobuf(file.read())

    feed = SubwayFeed(**data)
    assert isinstance(feed, SubwayFeed)
    assert isinstance(feed.extract_stop_dict(), dict)


@pytest.mark.parametrize("filename", TEST_PROTOBUFS)
def test_get(requests_mock, filename):
    """Test the get method creates the desired object."""
    with open(os.path.join(DATA_DIR, filename), "rb") as file:
        return_value = file.read()

    requests_mock.get(requests_mock_any, content=return_value)
    feed = SubwayFeed.get("1")  ## valid route but not used at all

    assert isinstance(feed, SubwayFeed)
    assert isinstance(feed.extract_stop_dict(), dict)


def test_trip_route_remap():
    """Test that the remapping works for a known route."""
    trip = models.Trip(trip_id="FAKE", start_time="01:00:00", start_date=20190101, route_id="5X")
    assert trip.route_id_mapped == "5"


def test_extract_dict_route_remap():
    """Test that the route remap is active for dict extraction."""
    sample_data = {
        "header": {"gtfs_realtime_version": "1.0", "timestamp": 0},
        "entity": [
            {
                "id": "X",
                "trip_update": {
                    "trip": {
                        "trip_id": "X",
                        "start_date": "20190726",
                        "route_id": "5X",
                    },
                    "stop_time_update": [{"arrival": {"time": 0}, "stop_id": "X"}],
                },
            }
        ],
    }
    stops = SubwayFeed(**sample_data).extract_stop_dict()
    assert len(stops["5"]["X"]) == 1


def test_extract_dict_elapsed_ignored():
    """Test that elapsed stops are ignored for stop extraction."""
    sample_data = {
        "header": {"gtfs_realtime_version": "1.0", "timestamp": 1},
        "entity": [
            {
                "id": "X",
                "trip_update": {
                    "trip": {"trip_id": "X", "start_date": "20190726", "route_id": "1"},
                    "stop_time_update": [
                        {"arrival": {"time": 0}, "stop_id": "IGNORED"},
                        {"arrival": {"time": 1}, "stop_id": "EXISTS"},
                    ],
                },
            }
        ],
    }

    stops = SubwayFeed(**sample_data).extract_stop_dict()
    assert "IGNORED" not in stops["1"]
    assert "EXISTS" in stops["1"]


def test_extract_dict_stalled_train_omitted():
    """Test that a stalled train is omitted from the stop extraction."""
    sample_data = {
        "header": {"gtfs_realtime_version": "1.0", "timestamp": 1699239196},
        "entity": [
            {
                "id": "000021F",
                "trip_update": {
                    "trip": {
                        "trip_id": "128000_F..S",
                        "start_time": "21:20:00",
                        "start_date": "20231105",
                        "route_id": "F",
                    },
                    "stop_time_update": [
                        {
                            "arrival": {"time": 1699239913},
                            "departure": {"time": 1699239913},
                            "stop_id": "D17S",
                        }
                    ],
                },
            },
            {
                "id": "000022F",
                "vehicle": {
                    "trip": {
                        "trip_id": "128000_F..S",
                        "start_time": "21:20:00",
                        "start_date": "20231105",
                        "route_id": "F",
                    },
                    "current_stop_sequence": 13,
                    "current_status": 1,
                    "timestamp": 1699238728,  # STALLED TRAIN
                    "stop_id": "G14S",
                },
            },
            {
                "id": "000025F",
                "trip_update": {
                    "trip": {
                        "trip_id": "129300_F..S",
                        "start_time": "21:33:00",
                        "start_date": "20231105",
                        "route_id": "F",
                    },
                    "stop_time_update": [
                        {
                            "arrival": {"time": 1699240511},
                            "departure": {"time": 1699240511},
                            "stop_id": "D17S",
                        }
                    ],
                },
            },
            {
                "id": "000026F",
                "vehicle": {
                    "trip": {
                        "trip_id": "129300_F..S",
                        "start_time": "21:33:00",
                        "start_date": "20231105",
                        "route_id": "F",
                    },
                    "current_stop_sequence": 10,
                    "current_status": 1,
                    "timestamp": 1699239183,
                    "stop_id": "G11S",
                },
            },
        ],
    }
    feed = SubwayFeed(**sample_data)

    stops_no_timeout = feed.extract_stop_dict(stalled_timeout=0)
    assert len(stops_no_timeout["F"]["D17S"]) == 2

    stops_default = feed.extract_stop_dict()  # stalled_timeout=90
    assert len(stops_default["F"]["D17S"]) == 1

    stops_long_timeout = feed.extract_stop_dict(stalled_timeout=900)
    assert len(stops_long_timeout["F"]["D17S"]) == 2


def test_empty_route_id():
    """Test the route functionality when the route id is a blacnk string.

    This uses example data i found in the wild.
    """
    trip = {"route_id": "", "start_date": "20191120", "trip_id": "060750_..N"}
    trip = models.Trip(**trip)
    assert trip.route_id_mapped == ""
    assert not trip.route_is_assigned


def test_malformed_departure_is_ignored():
    """Test that a stop_time_update with empty departure data is ignored."""
    sample_data = {
        "header": {"gtfs_realtime_version": "1.0", "timestamp": 1},
        "entity": [
            {
                "id": "X",
                "trip_update": {
                    "trip": {"trip_id": "X", "start_date": "20190726", "route_id": "1"},
                    "stop_time_update": [
                        {"departure": {}, "stop_id": "IGNORED"},
                        {"departure": {"time": 1}, "stop_id": "STOP1"},
                        {"departure": {"time": 2}, "stop_id": "STOP2"},
                    ],
                },
            }
        ],
    }

    stops = SubwayFeed(**sample_data).extract_stop_dict()
    assert "IGNORED" not in stops["1"]
    assert "STOP1" in stops["1"]
    assert "STOP2" in stops["1"]
