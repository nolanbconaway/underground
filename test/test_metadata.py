import pytest

from underground import metadata


@pytest.mark.parametrize(
    "fin,expected_url",
    [
        ("1", "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs"),
        (
            "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs",
            "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs",
        ),
        ["BUS", metadata.BUS_URL],
        [metadata.BUS_URL, metadata.BUS_URL]
    ],
)
def test_resolve_url(fin: str, expected_url: str):
    """Test that resolve_url works correctly."""
    url = metadata.resolve_url(fin)
    assert url == expected_url


def test_resolve_url_invalid():
    """Test that resolve_url raises for invalid route or url."""
    with pytest.raises(metadata.UnknownRouteOrURL):
        metadata.resolve_url("INVALID_ROUTE")
