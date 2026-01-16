# Python MTA Utilities

[![badge](https://github.com/nolanbconaway/underground/workflows/Push/badge.svg)](https://github.com/nolanbconaway/underground/actions)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/underground)](https://pypi.org/project/underground/)
[![PyPI](https://img.shields.io/pypi/v/underground)](https://pypi.org/project/underground/)

This is a set of Python utilities that I use to deal with [real-time NYC subway data](https://www.mta.info/developers).

I usually want to know when trains are going to depart a specific stop along a specific train line, so right now the tools are mostly for that. But I tried to write them to support arbitrary functionality.

The same code can also load the [bus time data](https://bustime.mta.info/wiki/Developers/GTFSRt), if you forgive
the mismatched naming conventions (e.g., a class called `SubwayFeed` holding a bus route).

## Install

``` sh
pip install underground
```

Or if you'd like to live dangerously:

``` sh
pip install git+https://github.com/nolanbconaway/underground.git#egg=underground
```

## Python API

Use the Python API like:

``` python
import os

from underground import metadata, SubwayFeed

ROUTE = 'Q'
feed = SubwayFeed.get(ROUTE)

# under the hood, the Q route is mapped to a URL. This call is equivalent:
URL = 'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-nqrw'
feed = SubwayFeed.get(URL)

# or
URL = metadata.resolve_url(ROUTE)
feed = SubwayFeed.get(URL)
```

### List train stops on each line

`feed.extract_stop_dict` will return a dictionary of dictionaries, like:

```python
>>> feed.extract_stop_dict()

{

  "route_1": {
    "stop_1": [datetime.datetime(...), datetime.datetime(...)], 
    "stop_2": [datetime.datetime(...), datetime.datetime(...)], 
    ...
  }, 
  "route_2": {
    "stop_1": [datetime.datetime(...), datetime.datetime(...)], 
    "stop_2": [datetime.datetime(...), datetime.datetime(...)], 
    ...
  }

}
```

## CLI

The `underground` command line tool is also installed with the package.

### `feed` 
```
$ underground feed --help
Usage: underground feed [OPTIONS] ROUTE_OR_URL

  Request an MTA feed via a route or URL.

  ROUTE_OR_URL may be either a feed URL or a route (which will be used to look
  up the feed url). ROUTE_OR_URL may also be "BUS" to access the bus feed.

  Examples (both access the same feed):

      underground feed Q --json > feed_nrqw.json

      URL='https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-nqrw' &&
      underground feed $URL --json > feed_nrqw.json

Options:
  --json                 Option to output the feed data as JSON. Otherwise
                         output will be bytes.

  -r, --retries INTEGER  Retry attempts in case of API connection failure.
                         Default 100.

  --help                 Show this message and exit.
```

### `stops` 

```
$ underground stops --help
Usage: underground stops [OPTIONS] ROUTE

  Print out train departure times for all stops on a subway line.

Options:
  -f, --format TEXT              strftime format for stop times. Use `epoch`
                                 for a unix timestamp.
  -r, --retries INTEGER          Retry attempts in case of API connection
                                 failure. Default 100.
  -t, --timezone TEXT            Output timezone. Ignored if --epoch. Default
                                 to NYC time.
  -s, --stalled-timeout INTEGER  Number of seconds between the last movement
                                 of a train and the API update before
                                 considering a train stalled. Default is 90 as
                                 recommended by the MTA. Numbers less than 1
                                 disable this check.
  --bus                          Set if the route is a bus route.
  --help                         Show this message and exit.
```

Stops are printed to stdout in the format `stop_id t1 t2 ... tn` .

```sh
$ underground stops Q | tail -2
Q05S 19:01 19:09 19:16 19:25 19:34 19:44 19:51 19:58
Q04S 19:03 19:11 19:18 19:27 19:36 19:46 19:53 20:00
```

If you know your stop id (stop IDs can be found in [stops.txt](http://web.mta.info/developers/data/nyct/subway/google_transit.zip)), you can grep the results:

``` sh
$ underground stops Q | grep Q05S
Q05S 19:09 19:16 19:25 19:34 19:44 19:51 19:58
```

If you don't know your stop, see below for a handy tool!

### `findstops` 

```
$ underground findstops --help
Usage: underground findstops [OPTIONS] QUERY...

  Find your stop ID.

  Query a location and look for your stop ID, like:

  $ underground findstops parkside av

Options:
  --json   Option to output the data as JSON. Otherwise will be human readable
           table.
  --buses  Option to also search bus stops. Slower.
  --help   Show this message and exit.
```

Enter the name of your stop and a table of stops with matching names will be returned.

```
$ underground findstops parkside
ID: D27N    Direction: NORTH    Lat/Lon: 40.655292, -73.961495    Name: PARKSIDE AV
ID: D27S    Direction: SOUTH    Lat/Lon: 40.655292, -73.961495    Name: PARKSIDE AV
```

Some names are ambiguous (try "fulton st"), for these you'll have to dig into the [metadata](https://www.mta.info/developers#static-gtfs-data) more carefully.

## Bus support

`underground` was initially written for the MTA subway feeds. However, contributors to the package identified that some level of bus support could be achieved with minimal maintenance burden. Currently, `underground` supports the bus feed on a best-effort basis. 

### Python API

All bus lines share the same feed, but lines can be ephemeral so `underground` cannot list them all in advance. So special care needs to be taken when resolving routes. Use the special `BUS` route to get the feed, and then find your route in the stops:

```py
from underground import SubwayFeed
feed = SubwayFeed.get("BUS")
stops = feed.extract_stop_dict()['BX30']
```

### CLI

Use the `BUS` identifier in the `feed` cli to obtain the bus feed. Querying a bus route will not work!

```sh
underground feed BUS
```

Similarly, use a `--bus` flag when obtaining stops to let underground know that it needs to retrieve the bus feed:

```sh
➜ underground stops --bus BX30 | tail -2
101735 18:42 18:57 19:12
104619 18:43 18:58 19:13
```

The bus stops lister in `findstops` is more expensive/time-consuming than the subway stops list, so use the `--bus` flag to indicate bus stops are desired:

```sh
➜ underground findstops --bus parkside
ID: D27N     Direction: NORTH    Data Source: subway       Lat/Lon: 40.655292,-73.961495  Name: PARKSIDE AV
ID: D27S     Direction: SOUTH    Data Source: subway       Lat/Lon: 40.655292,-73.961495  Name: PARKSIDE AV
ID: 301309   Direction: (BUS)    Data Source: buses_bk     Lat/Lon: 40.655129,-73.961122  Name: PARKSIDE AV/OCEAN AV
ID: 301310   Direction: (BUS)    Data Source: buses_bk     Lat/Lon: 40.655518,-73.960028  Name: PARKSIDE AV/FLATBUSH AV
ID: 301311   Direction: (BUS)    Data Source: buses_bk     Lat/Lon: 40.655815,-73.956542  Name: PARKSIDE AV/BEDFORD AV
ID: 303307   Direction: (BUS)    Data Source: buses_bk     Lat/Lon: 40.655257,-73.959894  Name: FLATBUSH AV/PARKSIDE AV
ID: 303981   Direction: (BUS)    Data Source: buses_bk     Lat/Lon: 40.655541,-73.956442  Name: BEDFORD AV/PARKSIDE AV
ID: 307645   Direction: (BUS)    Data Source: buses_bk     Lat/Lon: 40.654503,-73.961946  Name: OCEAN AV/PARKSIDE AV
ID: 308349   Direction: (BUS)    Data Source: buses_bk     Lat/Lon: 40.655139,-73.961837  Name: OCEAN AV/PARKSIDE AV
ID: 901089   Direction: (BUS)    Data Source: buses_bk     Lat/Lon: 40.654848,-73.961754  Name: PARKSIDE AV/OCEAN AV
```

