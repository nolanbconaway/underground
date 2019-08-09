"""Data model tests."""

import datetime
import json
import os

import pytz

from underground.dateutils import DEFAULT_TIMEZONE
from underground.models import SubwayFeed, UnixTimestamp

from . import DATA_DIR

# some data that i copied and edited
GTFS_DATA = json.loads(
    """
{
    "header": {
        "gtfs_realtime_version": "1.0",
        "timestamp": 0
    },
    "entity": [
        {
            "id": "0000077",
            "trip_update": {
                "trip": {
                    "trip_id": "043100_7..N",
                    "start_time": "07:11:00",
                    "start_date": "20190726",
                    "route_id": "7"
                },
                "stop_time_update": [
                    {
                        "arrival": {
                            "time": 0
                        },
                        "departure": {
                            "time": 0
                        },
                        "stop_id": "702N"
                    }
                ]
            }
        },
        {
            "id": "0000097",
            "trip_update": {
                "trip": {
                    "trip_id": "043600_7..N",
                    "start_time": "07:16:00",
                    "start_date": "20190726",
                    "route_id": "7"
                },
                "stop_time_update": [
                    {
                        "arrival": {
                            "time": 60
                        },
                        "departure": {
                            "time": 60
                        },
                        "stop_id": "702N"
                    }
                ]
            }
        }
    ]       
}
"""
)


def test_unix_timestamp():
    """Test that datetimes are handled correctly."""
    unix_ts = UnixTimestamp(time=0)
    epoch_time = datetime.datetime(1970, 1, 1, 0, 0, 0, 0, pytz.timezone("UTC"))
    assert unix_ts.time == epoch_time
    assert unix_ts.timestamp_nyc == epoch_time.astimezone(
        pytz.timezone(DEFAULT_TIMEZONE)
    )


def test_extract_stop_dict():
    """Test that the correct train times are extracted."""
    stops = SubwayFeed(**GTFS_DATA).extract_stop_dict()
    assert len(stops["7"]["702N"]) == 2


def test_on_actual_json():
    """Test the pydantic class works on a sample file.

    I got the file right from the MTA so this should be a realistic example.
    """
    with open(os.path.join(DATA_DIR, "sample_valid.json"), "r") as f:
        sample_data = json.load(f)

    feed = SubwayFeed(**sample_data)

    # I'm OK so long as there is no exception TBH.
    assert feed.entity is not None
    assert isinstance(feed.extract_stop_dict(), dict)
