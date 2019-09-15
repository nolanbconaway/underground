"""Test the feed submodule."""
import os
import time
from unittest import mock

import pytest

from underground import feed

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
@pytest.mark.parametrize("filename", TEST_PROTOBUFS)
def test_robust_retry_logic(feed_load_protobuf, feed_request, filename):
    """Test the request_robust retry logic."""
    # set up mocks
    feed_load_protobuf.side_effect = feed.EmptyFeedError

    with open(os.path.join(DATA_DIR, filename), "rb") as file:
        feed_request.return_value = file.read()

    # 1 retry should take at least 1 second
    time_1 = time.time()
    with pytest.raises(feed.EmptyFeedError):
        feed.request_robust(feed_id=16, retries=1, api_key="FAKE")
    assert time.time() - time_1 >= 1

    # and two should take two seconds
    time_1 = time.time()
    with pytest.raises(feed.EmptyFeedError):
        feed.request_robust(feed_id=16, retries=2, api_key="FAKE")
    assert time.time() - time_1 >= 2
