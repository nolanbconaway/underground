# Python MTA Utilities

This is a set of Python utilities that I use to deal with [real-time NYC subway data](https://datamine.mta.info/).

I usually want to know when trains are going to depart a specific stop along a specific train line, so right now the tools are only for that.

## Python API

To request data on when trains are arriving stops, you need to know [which feed to request](https://datamine.mta.info/list-of-feeds) for the train line you'd like. You'll also need an API key from the MTA, which is free.

Once you have your API key, use the Python API like:

```python
import os

from mta import mta, metadata

API_KEY = os.getenv('API_KEY')
ROUTE = 'Q'

# get feed id for the Q train route
FEED_ID = metadata.ROUTE_FEED_MAP[ROUTE]

# get all Q stops.
q_train_stops = mta.get_stops(API_KEY, FEED_ID)[ROUTE]
```

`get_stops` will return a dictionary of dictionaries, like:

```
{
  "route_1": {
    "stop_1": [DateTime(...), DateTime(...)],
    "stop_2": [DateTime(...), DateTime(...)],
    ...
  },
  "route_2": {
    "stop_1": [DateTime(...), DateTime(...)],
    "stop_2": [DateTime(...), DateTime(...)],
    ...
  }
}
```

## CLI

A command line tool is provided so you can access the upcoming stops from each train line.

Stops are printed to stdout in the format `stop_id  t1, t2, ... tn`.

```sh
$ export API_KEY='...'
$ mta stops Q | tail -2
Q05S  19:01 19:09 19:16 19:25 19:34 19:44 19:51 19:58
Q04S  19:03 19:11 19:18 19:27 19:36 19:46 19:53 20:00
$ mta stops --help     
Usage: mta stops [OPTIONS]
                 [N|M|R|4|L|GS|D|G|SI|J|Q|6|2|1|W|C|B|Z|H|7|A|E|FS|F|5]

  Print out train departure times for all stops on a subway line.

Options:
  -f, --format TEXT  strftime format for stop times.
  -e, --epoch        Option to print times as unix timestamps. If set --format
                     will be ignored.
  --retries INTEGER  Retry attempts in case of API connection failure. Default
                     100.
  --api-key TEXT     MTA API key. Will be read from $API_KEY if not provided.
  --help             Show this message and exit.
```

If you know your stop id (stop IDs can be found in [stops.txt](http://web.mta.info/developers/data/nyct/subway/google_transit.zip)), you can just grep the results:

```sh
$ mta stops Q | grep Q05S
Q05S  19:09 19:16 19:25 19:34 19:44 19:51 19:58
```