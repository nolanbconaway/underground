"""Setup."""

from pathlib import Path

from setuptools import find_packages, setup

THIS_DIRECTORY = Path(__file__).resolve().parent
VERSION = (THIS_DIRECTORY / "src" / "underground" / "version").read_text().strip()

INSTALL_REQUIRES = [
    "requests>=2.22",
    "google~=2.0",
    "gtfs-realtime-bindings==0.0.6",
    "protobuf>=3.19.6,<=3.20.3",
    "protobuf3-to-dict>=0.1.5",
    "click~=7.0",
    "pydantic~=0.31.1",
    "pytz>=2019.2",
]

DEV_REQUIRES = [
    "pytest>=5.0",
    "tox>=3.13",
    "black==19.10b0",
    "pytest-cov>=2.8",
    "codecov>=2.0",
    "requests-mock>=1.7.0",
]

# use readme as long description
LONG_DESCRIPTION = (THIS_DIRECTORY / "readme.md").read_text()

setup(
    name="underground",
    version=VERSION,
    description="Utilities for NYC's realtime MTA data feeds.",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    author="Nolan Conaway",
    author_email="nolanbconaway@gmail.com",
    url="https://github.com/nolanbconaway/underground",
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    keywords=["nyc", "transit", "subway", "command-line", "cli"],
    license="MIT",
    package_dir={"": "src"},
    packages=find_packages("src"),
    install_requires=INSTALL_REQUIRES,
    extras_require=dict(dev=DEV_REQUIRES),
    entry_points={"console_scripts": ["underground = underground.cli.cli:entry_point"]},
    package_data={"underground": ["version"]},
)
