# Python MTA Utilities

[![GitHub Actions status](https://github.com/nolanbconaway/underground/workflows/Main%20Workflow/badge.svg)](https://github.com/nolanbconaway/underground/actions)
[![codecov](https://codecov.io/gh/nolanbconaway/underground/branch/master/graph/badge.svg)](https://codecov.io/gh/nolanbconaway/underground)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/underground)](https://pypi.org/project/underground/)
[![PyPI](https://img.shields.io/pypi/v/underground)](https://pypi.org/project/underground/)

This is a set of Python utilities that I use to deal with [real-time NYC subway data](https://datamine.mta.info/).

I usually want to know when trains are going to depart a specific stop along a specific train line, so right now the tools are mostly for that. But I tried to write them to support arbitrary functionality.

## Install

``` sh
pip install underground
```

Or if you'd like to live dangerously:

``` sh
pip install git+https://github.com/nolanbconaway/underground.git#egg=underground
```

To request data from the MTA, you'll also need a free API key.
[Register here](https://datamine.mta.info/user/register).

## Python API

Once you have your API key, use the Python API like:

``` python
import os

from underground import metadata, SubwayFeed

API_KEY = os.getenv('MTA_API_KEY')
ROUTE = 'Q'

# get feed id for the Q train route
FEED_ID = metadata.get_feed_id(ROUTE)

# request and serialize the feed data.
feed = SubwayFeed.get(FEED_ID, api_key=API_KEY)

# request will automatically try to read from $MTA_API_KEY if a key is not provided,
# so this also works:
feed = SubwayFeed.get(FEED_ID)

# extract train stops on each line
q_train_stops = feed.extract_stop_dict()[ROUTE]
```

`feed.extract_stop_dict` will return a dictionary of dictionaries, like:

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

> Note: future functionality to be written around the `SubwayFeed` class.

## CLI

The `underground` command line tool is also installed with the package.

    $ underground --help
    Usage: underground [OPTIONS] COMMAND [ARGS]...

      Command line handlers for MTA realtime data.

    Options:

      --help  Show this message and exit.

      feed       Request an MTA feed.
      findstops  Find your stop ID.
      stops      Print out train departure times for all stops on a subway line.

### `feed` 

    $ underground feed --help
    Usage: underground feed [OPTIONS] [1|2|36|11|16|51|21|26|31]

      Request an MTA feed.

    Options:

      --api-key TEXT         MTA API key. Will be read from $MTA_API_KEY if not
                             provided.
      --json                 Option to output the feed data as JSON. Otherwise
                             output will be bytes.
      -r, --retries INTEGER  Retry attempts in case of API connection failure.
                             Default 100.
      --help                 Show this message and exit.

Use it like

    $ export MTA_API_KEY='...'
    $ underground feed 16 --json > feed_16.json

### `stops` 

    $ underground stops --help
    Usage: underground stops [OPTIONS] [H|M|D|1|Z|A|N|GS|SI|J|G|Q|L|B|R|F|E|2|7|W|
                             6|4|C|5|FS]
        
      Print out train departure times for all stops on a subway line.

    Options:

      -f, --format TEXT      strftime format for stop times. Use `epoch` for a
                             unix timestamp.
      -r, --retries INTEGER  Retry attempts in case of API connection failure.
                             Default 100.
      --api-key TEXT         MTA API key. Will be read from $MTA_API_KEY if not
                             provided.
      -t, --timezone TEXT    Output timezone. Ignored if --epoch. Default to NYC
                             time.
      --help                 Show this message and exit.

Stops are printed to stdout in the format `stop_id t1 t2 ... tn` .

``` sh
$ export MTA_API_KEY='...'
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

    $ underground findstops --help
    Usage: underground findstops [OPTIONS] QUERY...

      Find your stop ID.

      Query a location and look for your stop ID, like:

      $ underground findstops parkside av

    Options:

      --json  Option to output the data as JSON. Otherwise will be human readable
              table.

      --help  Show this message and exit.

Enter the name of your stop and a table of stops with matching names will be returned.

    $ underground findstops parkside
    ID: D27N    Direction: NORTH    Lat/Lon: 40.655292, -73.961495    Name: PARKSIDE AV
    ID: D27S    Direction: SOUTH    Lat/Lon: 40.655292, -73.961495    Name: PARKSIDE AV

Some names are ambiguous (try "fulton st"), for these you'll have to dig into the [metadata](http://web.mta.info/developers/data/nyct/subway/google_transit.zip) more carefully.

## Todo

None of this is particularly important, I am happy with the API at the moment.

*   [ ] Better exception printing from click.
*   [ ] Pypi?
*   [ ] Markdown auto format. Check as a part of the build process.
*   [x] Add some tooling to make finding your stop easier.
*   [ ] Add method to SubwayFeed which counts trains per line/direction.

