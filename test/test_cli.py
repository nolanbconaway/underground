"""Test the CLI."""
import io
import json
import os
import subprocess
import zipfile

import pytest
from click.testing import CliRunner
from requests_mock import ANY as requests_mock_any

from underground import __version__ as underground_version
from underground.cli import feed as feed_cli
from underground.cli import findstops as findstops_cli
from underground.cli import stops as stops_cli
from underground.cli import version as version_cli
from underground.feed import load_protobuf
from underground.models import SubwayFeed

from . import DATA_DIR, TEST_PROTOBUFS


def test_version():
    """Check that the version CLI works."""
    runner = CliRunner()
    result = runner.invoke(version_cli.main)
    assert result.exit_code == 0
    assert underground_version in result.output


def test_stops_epoch(monkeypatch):
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
    monkeypatch.setattr(
        "underground.SubwayFeed.get", lambda *x, **y: SubwayFeed(**sample_data)
    )
    runner = CliRunner()
    result = runner.invoke(stops_cli.main, ["1", "-f", "epoch"])
    assert result.exit_code == 0
    assert "ONE 0" in result.output
    assert "TWO 1 3" in result.output


def test_stops_format(monkeypatch):
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

    monkeypatch.setattr(
        "underground.SubwayFeed.get", lambda *x, **y: SubwayFeed(**sample_data)
    )
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


def test_stops_timezone(monkeypatch):
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

    monkeypatch.setattr(
        "underground.SubwayFeed.get", lambda *x, **y: SubwayFeed(**sample_data)
    )
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


@pytest.mark.parametrize("filename", TEST_PROTOBUFS)
def test_feed_bytes(requests_mock, filename):
    """Test the bytes output option."""
    with open(os.path.join(DATA_DIR, filename), "rb") as file:
        requests_mock.get(requests_mock_any, content=file.read())

    runner = CliRunner()
    result = runner.invoke(feed_cli.main, ["1", "--api-key", "FAKE"])
    assert result.exit_code == 0
    assert "entity" in load_protobuf(result.stdout_bytes)


@pytest.mark.parametrize("filename", TEST_PROTOBUFS)
def test_feed_json(requests_mock, filename):
    """Test the json output option."""
    with open(os.path.join(DATA_DIR, filename), "rb") as file:
        requests_mock.get(requests_mock_any, content=file.read())

    runner = CliRunner()
    result = runner.invoke(feed_cli.main, ["1", "--json", "--api-key", "FAKE"])
    assert result.exit_code == 0
    assert "entity" in json.loads(result.output)


@pytest.mark.parametrize("args", [["PARKSIDE"], ["parkside"], ["PARKSIDE", "av"]])
def test_stopstxt(monkeypatch, args):
    """Test the json output option."""
    with open(os.path.join(DATA_DIR, "google_transit.zip"), "rb") as file:
        content = zipfile.ZipFile(io.BytesIO(file.read()))

    monkeypatch.setattr(
        "underground.cli.findstops.request_data", lambda: content,
    )
    runner = CliRunner()
    result = runner.invoke(findstops_cli.main, args)
    assert result.exit_code == 0
    assert "D27N" in result.output
    assert "D27S" in result.output


@pytest.mark.parametrize("args", [["PARKSIDE"], ["parkside"], ["PARKSIDE", "av"]])
def test_stopstxt_json(monkeypatch, args):
    """Test the json output option."""
    with open(os.path.join(DATA_DIR, "google_transit.zip"), "rb") as file:
        content = zipfile.ZipFile(io.BytesIO(file.read()))

    monkeypatch.setattr(
        "underground.cli.findstops.request_data", lambda: content,
    )
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
        ("python", "-m", "underground.cli", "version", "--help"),
    ],
)
def test_cli_mains(command):
    """Test that the mains return valid help info."""
    output = subprocess.check_output(command)
    assert "help" in output.decode()


def test_findstop_request(requests_mock):
    """Mock request to test the findstops function."""
    with open(os.path.join(DATA_DIR, "google_transit.zip"), "rb") as file:
        zip_data = file.read()

    requests_mock.get(requests_mock_any, content=zip_data)

    findstops_cli.request_data()
