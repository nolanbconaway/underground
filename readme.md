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

  ROUTE_OR_URL may be either a feed URL or a route (which will be used to
  look up the feed url).

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
Usage: underground stops [OPTIONS] [H|M|D|1|Z|A|N|GS|SI|J|G|Q|L|B|R|F|E|2|7|W|
                          6|4|C|5|FS]
    
  Print out train departure times for all stops on a subway line.

Options:

  -f, --format TEXT      strftime format for stop times. Use `epoch` for a
                          unix timestamp.
  -r, --retries INTEGER  Retry attempts in case of API connection failure.
                          Default 100.
  -t, --timezone TEXT    Output timezone. Ignored if --epoch. Default to NYC
                          time.
  -s, --stalled-timeout INTEGER  Number of seconds between the last movement
                                 of a train and the API update before
                                 considering a train stalled. Default is 90 as
                                 recommended by the MTA. Numbers less than 1
                                 disable this check.
  --help                 Show this message and exit.
```

Stops are printed to stdout in the format `stop_id t1 t2 ... tn` .

``` sh
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
