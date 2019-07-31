"""Dateutils tests."""

import pendulum

from mta_realtime import dateutils


def test_current_time_datetime():
    """Test that current time returns a datetime by default."""
    assert isinstance(dateutils.current_time(), pendulum.DateTime)


def test_current_time_epoch_int():
    """Test that current time returns an integer if epoch is specified.."""
    assert isinstance(dateutils.current_time(epoch=True), int)


def test_current_time_working():
    """Test that current time is later if called in the future."""
    t1 = dateutils.current_time()
    t2 = dateutils.current_time()
    assert t2 > t1


def test_epoch_to_datetime():
    """Test that epoch_to_datetime returns datetime."""
    assert isinstance(dateutils.epoch_to_datetime(0), pendulum.DateTime)


def test_datetime_to_epoch():
    """Test that datetime_to_epoch returns int."""
    dttm = dateutils.current_time()
    assert isinstance(dateutils.datetime_to_epoch(dttm), int)


def test_datetime_epoch_roundtrip():
    """Test that we can move from datetime to epoch and back."""
    # epoch -> datetime -> epoch
    epoch = 0
    dttm = dateutils.epoch_to_datetime(epoch)
    assert epoch == dateutils.datetime_to_epoch(dttm)

    # datetime -> epoch -> datetime
    dttm = dateutils.current_time().replace(microsecond=0)
    epoch = dateutils.datetime_to_epoch(dttm)
    assert dateutils.epoch_to_datetime(epoch) == dttm


def test_datetime_to_timestring():
    """Test that datetime_to_timestring returns string."""
    dttm = dateutils.current_time()
    assert isinstance(dateutils.datetime_to_timestring(dttm), str)
