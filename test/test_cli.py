"""Test the CLI."""
import json
import os
from unittest import mock

from click.testing import CliRunner

from underground.cli import feed as feed_cli
from underground.cli import stops as stops_cli
from underground.models import SubwayFeed

from . import DATA_DIR


@mock.patch("underground.models.SubwayFeed.request")
def test_stops_epoch(feed_request):
    """Test the epoch handler in the stops cli."""
    with open(os.path.join(DATA_DIR, "sample_edited.json"), "r") as f:
        feed_request.return_value = SubwayFeed(**json.load(f))

    runner = CliRunner()
    result = runner.invoke(stops_cli.main, ["7", "-f", "epoch"])
    assert result.exit_code == 0
    assert "702N 0 60" in result.output


@mock.patch("underground.models.SubwayFeed.request")
def test_stops_format(feed_request):
    """Test the format handler in the stops cli."""
    with open(os.path.join(DATA_DIR, "sample_edited.json"), "r") as f:
        feed_request.return_value = SubwayFeed(**json.load(f))

    runner = CliRunner()

    # year
    result = runner.invoke(stops_cli.main, ["7", "-f", "%Y", "-t", "UTC"])
    assert result.exit_code == 0
    assert "702N 1970 1970" in result.output

    # hour
    result = runner.invoke(stops_cli.main, ["7", "-f", "%H", "-t", "UTC"])
    assert result.exit_code == 0
    assert "702N 00 00" in result.output


@mock.patch("underground.models.SubwayFeed.request")
def test_stops_timezone(feed_request):
    """Test the timezone handler in the stops cli."""
    with open(os.path.join(DATA_DIR, "sample_edited.json"), "r") as f:
        feed_request.return_value = SubwayFeed(**json.load(f))

    runner = CliRunner()

    # in hong kong time
    result = runner.invoke(stops_cli.main, ["7", "-f", "%Y", "-t", "Asia/Hong_Kong"])
    assert result.exit_code == 0
    assert "702N 1970 1970" in result.output

    # in nyc time
    result = runner.invoke(stops_cli.main, ["7", "-f", "%Y"])
    assert result.exit_code == 0
    assert "702N 1969 1969" in result.output
