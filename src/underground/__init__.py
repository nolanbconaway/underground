"""A realtime MTA module."""
from pathlib import Path

from .models import SubwayFeed

__version__ = (Path(__file__).resolve().parent / "version").read_text().strip()

__all__ = ["SubwayFeed", "__version__"]
