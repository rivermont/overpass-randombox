#!/usr/bin/env python3

import requests
from random import uniform

# Sides of the square bounding box, in degrees
size = 0.005

# Set this to False if you want to get areas without content
# This will mostly be empty ocean.
verify_exists = True

# Length of time (in seconds) to wait for data from the server
timeout = 200


class SizeError(Exception):
    """Raised when a request returns a weird file size."""
    pass


def rand_lat():
    return uniform(-90, 90)


def rand_lon():
    return uniform(-180, 180)


def get_box(lat0, lon0, inc):
    lat1 = lat0 + inc
    lon1 = lon0 + inc
    return "{0}, {1}, {2}, {3}".format(lat0, lon0, lat1, lon1)


def main():
    searching = True
    outfile = ""

    while searching:

        lat = rand_lat()
        lon = rand_lon()

        box = get_box(lat, lon, size)
        outfile = "{0}_{1}.osm".format(lat, lon)

        query = """[out:xml][timeout:{0}];(node({1});way({1});rel({1}););out meta;>;out meta qt;""".format(timeout, box)
        response = requests.get("""http://overpass-api.de/api/interpreter?data={0}""".format(query))

        if response.status_code != 200:
            print("Bad HTTP status code {0}".format(response.status_code))
            continue

        if verify_exists:
            blank = 267
            if len(response.content) == blank:
                # XML response is an empty shell
                continue
            elif len(response.content) < blank:
                # Response has less content than a blank document; something's wrong
                raise SizeError
            elif len(response.content) > blank:
                # Response has content
                searching = False
        else:
            searching = False

    # Loop is exited; must have found a good area

    with open(outfile, "wb+") as f:
        print("Writing to {0}".format(outfile))
        f.write(response.content)


if __name__ == "__main__":
    main()
    print("Done!")
