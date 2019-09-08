# Test Data

This directory contains test data files. The contents are:

* `sample_edited.json` : Some JSON which should be valid. It is dummy data that I edited, so it only contains a subset of the usual data. But I _do_ know what is in there so it can be used to test results explicitly.
* `sample_valid.json` : I queried the MTA api and saved a payload of JSON. I don't know whats in here but its an example of valid "real-world" data. This is _not_ the same as the protobuf data.
* `sample_valid.protobuf` : I queried the MTA api and saved a protobuf file. I don't know whats in here but its an example of valid "real-world" data. This is _not_ the same as the JSON data.
* `google_transit.zip` : A ZIP file containing metadata, downloaded on Sept 8 2019 from http://web.mta.info/developers/data/nyct/subway/google_transit.zip

