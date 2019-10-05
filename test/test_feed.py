"""Test the feed submodule."""
import os
import time
from unittest import mock

import pytest
import requests

from underground import feed, metadata

from . import DATA_DIR, TEST_PROTOBUFS


@pytest.mark.parametrize("filename", TEST_PROTOBUFS)
def test_load_protobuf(filename):
    """Test that protobuf loader works."""
    with open(os.path.join(DATA_DIR, filename), "rb") as file:
        sample_bytes = file.read()

    data = feed.load_protobuf(sample_bytes)
    assert "entity" in data
    assert "header" in data


@mock.patch("underground.feed.request")
@mock.patch("underground.feed.load_protobuf")
@pytest.mark.parametrize("retries", [0, 1, 2])
def test_robust_retry_logic(feed_load_protobuf, feed_request, retries):
    """Test the request_robust retry logic."""
    # set up mocks
    feed_load_protobuf.side_effect = feed.EmptyFeedError

    with open(os.path.join(DATA_DIR, TEST_PROTOBUFS[0]), "rb") as file:
        feed_request.return_value = file.read()

    time_1 = time.time()
    with pytest.raises(feed.EmptyFeedError):
        feed.request_robust(feed_id=16, retries=retries, api_key="FAKE")
    elapsed = time.time() - time_1

    assert elapsed >= retries
    assert elapsed < (retries + 1)


@mock.patch("protobuf_to_dict.protobuf_to_dict")
@pytest.mark.parametrize("dict_data", [dict(), dict(a=1)])
def test_emptyfeederror(protobuf_to_dict, dict_data):
    """Test that empty feed is raised."""
    protobuf_to_dict.return_value = dict_data

    with open(os.path.join(DATA_DIR, TEST_PROTOBUFS[0]), "rb") as file:
        protobuf_data = file.read()

    with pytest.raises(feed.EmptyFeedError):
        feed.load_protobuf(protobuf_data)


def test_request_invalid_feed():
    """Test that request raises value error for an invalid feed."""
    with pytest.raises(ValueError):
        feed.request("NOT REAL")


def test_request_no_api_key(monkeypatch):
    """Test that request raises value error when no api key is available."""
    monkeypatch.delenv("MTA_API_KEY", raising=False)

    with pytest.raises(ValueError):
        feed.request(next(iter(metadata.VALID_FEED_IDS)))


@pytest.mark.parametrize("ret_code", [200, 500])
def test_request_elaborate_mocks(monkeypatch, ret_code):
    """Test the full request function with a lot of mocking."""
    feed_id = next(iter(metadata.VALID_FEED_IDS))

    class Result(object):
        def __init__(self, ret_code):
            self.ret_code = ret_code

        def raise_for_status(self):
            if self.ret_code != 200:
                raise requests.HTTPError

        @property
        def content(self):
            return ":-)"

    monkeypatch.setattr("requests.get", lambda *a, **k: Result(ret_code))
    monkeypatch.setenv("MTA_API_KEY", "FAKE")
    if ret_code != 200:
        with pytest.raises(requests.HTTPError):
            feed.request(feed_id)
    else:
        feed.request(feed_id)
