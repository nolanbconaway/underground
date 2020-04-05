"""Test the feed submodule."""
import os
import time

import pytest
import requests
from requests_mock import ANY as requests_mock_any

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


@pytest.mark.parametrize("retries", [0, 1, 2])
def test_robust_retry_logic(requests_mock, monkeypatch, retries):
    """Test the request_robust retry logic."""
    with open(os.path.join(DATA_DIR, TEST_PROTOBUFS[0]), "rb") as file:
        return_value = file.read()

    def mock_load_protobuf(*a):
        raise feed.EmptyFeedError

    # set up mocks
    monkeypatch.setattr("underground.feed.load_protobuf", mock_load_protobuf)
    requests_mock.get(requests_mock_any, content=return_value)

    time_1 = time.time()
    with pytest.raises(feed.EmptyFeedError):
        feed.request_robust("1", retries=retries, api_key="FAKE")
    elapsed = time.time() - time_1

    assert elapsed >= retries
    assert elapsed < (retries + 1)


@pytest.mark.parametrize("dict_data", [dict(), dict(a=1)])
def test_emptyfeederror(monkeypatch, dict_data):
    """Test that empty feed is raised."""
    monkeypatch.setattr("protobuf_to_dict.protobuf_to_dict", lambda x: dict_data)

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
        feed.request(next(iter(metadata.VALID_FEED_URLS)))


@pytest.mark.parametrize("ret_code", [200, 500])
def test_request_raise_status(requests_mock, ret_code):
    """Test the request raise status conditional."""
    feed_url = next(iter(metadata.VALID_FEED_URLS))
    requests_mock.get(requests_mock_any, content="".encode(), status_code=ret_code)
    if ret_code != 200:
        with pytest.raises(requests.HTTPError):
            feed.request(feed_url, api_key="FAKE")
    else:
        feed.request(feed_url, api_key="FAKE")
