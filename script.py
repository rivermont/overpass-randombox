#!/usr/bin/env python3

import requests
import gpxpy.gpx
from random import uniform

# Sides of the square bounding box, in degrees
size = 0.01

# Set this to False if you want to get areas without content
# This will mostly be empty ocean.
verify_exists = True

# Length of time (in seconds) to wait for data from the server
timeout = 200


class UnknownError(Exception):
    pass


def trunc(num, digits=5):
    """Truncates a float 'num' to 'digits' number of trailing significant digits.
    trunc(57.136658951830555, 4) -> 47.1366"""
    s = str(num)
    l = s.split('.')
    a = l[0]
    b = l[1]
    del l
    c = b[:digits]
    d = a + '.' + c
    if str(d) in s:
        return float(d)
    else:
        raise UnknownError


def rand_lat():
    return trunc(uniform(-90, 90))


def rand_lon():
    return trunc(uniform(-180, 180))


def get_box(lat0, lon0, inc):
    lat1 = lat0 + inc
    lon1 = lon0 + inc
    return "{0}, {1}, {2}, {3}".format(lat0, lon0, lat1, lon1)


def make_gpx(lat0, lon0, lat1, lon1):
    """Returns an XML GPX object, a rectangle with
    corners of (lat0, lon0) and (lat1, lon1)."""
    gpx = gpxpy.gpx.GPX()


def do():
    """Picks a random coordinate on the map,"""
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
                raise UnknownError
            elif len(response.content) > blank:
                # Response has content
                searching = False
        else:
            searching = False

    # Loop is exited; must have found a good area

    print(box)
    with open(outfile, "wb+") as f:
        print("Writing to {0}".format(outfile))
        f.write(response.content)


def main():
    i = 5
    while i:
        do()
        i += -1


if __name__ == "__main__":
    main()
    print("Done!")
