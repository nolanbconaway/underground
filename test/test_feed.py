"""Test the feed submodule."""

import os

from underground import feed

from . import DATA_DIR


def test_load_protobuf():
    """Test that protobuf loader works."""
    with open(os.path.join(DATA_DIR, "sample_valid.protobuf"), "rb") as f:
        sample_bytes = f.read()

    data = feed.load_protobuf(sample_bytes)
    assert "entity" in data
    assert "header" in data
