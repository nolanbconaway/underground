"""Data model tests."""
import datetime
import json
import os
from unittest import mock

import pytest
import pytz

from underground import SubwayFeed, models
from underground.dateutils import DEFAULT_TIMEZONE
from underground.feed import load_protobuf

from . import DATA_DIR


def test_unix_timestamp():
    """Test that datetimes are handled correctly."""
    unix_ts = models.UnixTimestamp(time=0)
    epoch_time = datetime.datetime(1970, 1, 1, 0, 0, 0, 0, pytz.timezone("UTC"))
    assert unix_ts.time == epoch_time
    assert unix_ts.timestamp_nyc == epoch_time.astimezone(
        pytz.timezone(DEFAULT_TIMEZONE)
    )


def test_extract_stop_dict():
    """Test that the correct train times are extracted.
    
    Going to use a dummy JSON file that I have edited.
    """
    with open(os.path.join(DATA_DIR, "sample_edited.json"), "r") as file:
        sample_data = json.load(file)
    stops = SubwayFeed(**sample_data).extract_stop_dict()
    assert len(stops["7"]["702N"]) == 2


def test_on_actual_json():
    """Test the pydantic class works on a sample file.

    I got the file right from the MTA so this should be a realistic example.
    """
    with open(os.path.join(DATA_DIR, "sample_valid.json"), "r") as file:
        sample_data = json.load(file)

    feed = SubwayFeed(**sample_data)

    # I'm OK so long as there is no exception TBH.
    assert feed.entity is not None
    assert isinstance(feed.extract_stop_dict(), dict)


@pytest.mark.parametrize(
    "filename",
    [
        "feed_1_sample.protobuf",
        "feed_51_sample.protobuf",
        "feed_26_sample.protobuf",
        "feed_21_sample.protobuf",
        "feed_31_sample.protobuf",
        "feed_36_sample.protobuf",
        "feed_2_sample.protobuf",
        "feed_16_sample.protobuf",
        "feed_11_sample.protobuf",
    ],
)
def test_on_sample_protobufs(filename):
    """Make sure the model can load up one sample from all the feeds."""
    with open(os.path.join(DATA_DIR, filename), "rb") as file:
        data = load_protobuf(file.read())

    feed = SubwayFeed(**data)
    assert isinstance(feed, SubwayFeed)
    assert isinstance(feed.extract_stop_dict(), dict)


@mock.patch("underground.feed.request")
def test_get(feed_request):
    """Test the get method creates the desired object."""
    with open(os.path.join(DATA_DIR, "feed_16_sample.protobuf"), "rb") as file:
        feed_request.return_value = file.read()

    feed = SubwayFeed.get(16)
    assert isinstance(feed, SubwayFeed)
    assert isinstance(feed.extract_stop_dict(), dict)
