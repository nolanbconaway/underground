"""Dateutils tests."""

import json

from underground.models import SubwayFeed

# some data that i copied and edited
GTFS_DATA = json.loads(
    """
{
    "header": {
        "gtfs_realtime_version": "1.0",
        "timestamp": 1564142408
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


def test_extract_stop_dict():
    """Test that the correct train times are extracted."""
    res = SubwayFeed(**GTFS_DATA).extract_stop_dict()
    assert len(res["7"]["702N"]) == 2
