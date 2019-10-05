"""Test the CLI."""
import io
import json
import os
import subprocess
import zipfile
from unittest import mock

import pytest
from click.testing import CliRunner

from underground.cli import feed as feed_cli
from underground.cli import findstops as findstops_cli
from underground.cli import stops as stops_cli
from underground.feed import load_protobuf
from underground.models import SubwayFeed

from . import DATA_DIR, TEST_PROTOBUFS


@mock.patch("underground.models.SubwayFeed.get")
def test_stops_epoch(subwayfeed_get):
    """Test the epoch handler in the stops cli."""
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
    subwayfeed_get.return_value = SubwayFeed(**sample_data)

    runner = CliRunner()
    result = runner.invoke(stops_cli.main, ["1", "-f", "epoch"])
    assert result.exit_code == 0
    assert "ONE 0" in result.output
    assert "TWO 1 3" in result.output


@mock.patch("underground.models.SubwayFeed.get")
def test_stops_format(subwayfeed_get):
    """Test the format handler in the stops cli."""
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

    subwayfeed_get.return_value = SubwayFeed(**sample_data)
    runner = CliRunner()

    # year
    result = runner.invoke(stops_cli.main, ["1", "-f", "%Y", "-t", "UTC"])
    assert result.exit_code == 0
    assert "ONE 1970" in result.output
    assert "TWO 1970 1970" in result.output

    # hour
    result = runner.invoke(stops_cli.main, ["1", "-f", "%H", "-t", "UTC"])
    assert result.exit_code == 0
    assert "ONE 00" in result.output
    assert "TWO 00 00" in result.output


@mock.patch("underground.models.SubwayFeed.get")
def test_stops_timezone(subwayfeed_get):
    """Test the timezone handler in the stops cli."""
    sample_data = {
        "header": {"gtfs_realtime_version": "1.0", "timestamp": 0},
        "entity": [
            {
                "id": "1",
                "trip_update": {
                    "trip": {"trip_id": "X", "start_date": "20190726", "route_id": "1"},
                    "stop_time_update": [
                        {"arrival": {"time": 1}, "stop_id": "ONE"},
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

    subwayfeed_get.return_value = SubwayFeed(**sample_data)
    runner = CliRunner()

    # in hong kong time
    result = runner.invoke(stops_cli.main, ["1", "-f", "%Y", "-t", "Asia/Hong_Kong"])
    assert result.exit_code == 0
    assert "ONE 1970" in result.output
    assert "TWO 1970 1970" in result.output

    # in nyc time
    result = runner.invoke(stops_cli.main, ["1", "-f", "%Y"])
    assert result.exit_code == 0
    assert "TWO 1969 1969" in result.output
    assert "ONE 1969" in result.output


@mock.patch("underground.feed.request")
@pytest.mark.parametrize("filename", TEST_PROTOBUFS)
def test_feed_bytes(feed_request, filename):
    """Test the bytes output option."""
    with open(os.path.join(DATA_DIR, filename), "rb") as file:
        feed_request.return_value = file.read()

    runner = CliRunner()
    result = runner.invoke(feed_cli.main, ["16"])
    assert result.exit_code == 0
    assert "entity" in load_protobuf(result.stdout_bytes)


@mock.patch("underground.feed.request")
@pytest.mark.parametrize("filename", TEST_PROTOBUFS)
def test_feed_json(feed_request, filename):
    """Test the json output option."""
    with open(os.path.join(DATA_DIR, filename), "rb") as file:
        feed_request.return_value = file.read()

    runner = CliRunner()
    result = runner.invoke(feed_cli.main, ["16", "--json"])
    assert result.exit_code == 0
    assert "entity" in json.loads(result.output)


@mock.patch("underground.cli.findstops.request_data")
@pytest.mark.parametrize("args", [["PARKSIDE"], ["parkside"], ["PARKSIDE", "av"]])
def test_stopstxt(request_fun, args):
    """Test the json output option."""
    with open(os.path.join(DATA_DIR, "google_transit.zip"), "rb") as file:
        request_fun.return_value = zipfile.ZipFile(io.BytesIO(file.read()))
    runner = CliRunner()
    result = runner.invoke(findstops_cli.main, args)
    assert result.exit_code == 0
    assert "D27N" in result.output
    assert "D27S" in result.output


@mock.patch("underground.cli.findstops.request_data")
@pytest.mark.parametrize("args", [["PARKSIDE"], ["parkside"], ["PARKSIDE", "av"]])
def test_stopstxt_json(request_fun, args):
    """Test the json output option."""
    with open(os.path.join(DATA_DIR, "google_transit.zip"), "rb") as file:
        request_fun.return_value = zipfile.ZipFile(io.BytesIO(file.read()))
    runner = CliRunner()
    result = runner.invoke(findstops_cli.main, args + ["--json"])
    assert result.exit_code == 0

    for stop in json.loads(result.output):
        assert "direction" in stop
        assert "stop_id" in stop
        assert "stop_name" in stop


@pytest.mark.parametrize(
    "command",
    [
        ("python", "-m", "underground.cli", "--help"),
        ("python", "-m", "underground.cli.feed", "--help"),
        ("python", "-m", "underground.cli", "feed", "--help"),
        ("python", "-m", "underground.cli.stops", "--help"),
        ("python", "-m", "underground.cli", "stops", "--help"),
        ("python", "-m", "underground.cli.findstops", "--help"),
        ("python", "-m", "underground.cli", "findstops", "--help"),
    ],
)
def test_cli_mains(command):
    """Test that the mains return valid help info."""
    output = subprocess.check_output(command)
    assert "help" in output.decode()
