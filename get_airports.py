from pprint import pprint

import populartimes
import requests
from io import StringIO
import csv
import more_itertools
import sys

import time

from credentials import API_KEY
from googleplaces import GooglePlaces, types, lang
import percache

google_places = GooglePlaces(API_KEY)
cache = percache.Cache("./times_cache")


def load_airports():
    data_source = "https://raw.githubusercontent.com/jpatokal/openflights/master/data/airports.dat"
    fieldnames = ["Airline ID", "Name", "City", "Country", "IATA", "ICAO", "Latitude", "Longitude", "Altitude",
                  "Timezone", "DST", "Tz database time zone", "Type", "Source"]
    resp = requests.get(data_source)
    csv_file = StringIO(resp.text)
    reader = csv.DictReader(csv_file, fieldnames=fieldnames)
    yield from (dict(airport) for airport in reader if airport["Country"] == "United States")
    # yield from reader


@cache
def get_airport_popular_times(airport):
    "https://maps.googleapis.com/maps/api/js?key=YOUR_API_KEY"
    print("getting", file=sys.stderr)
    places = google_places.nearby_search(keyword="IATA: " + airport["IATA"],
                                         lat_lng={'lat': airport["Latitude"], 'lng': airport["Longitude"]},
                                         radius=10000,
                                         types=[types.TYPE_AIRPORT]).places
    if len(places):
        # todo: cache ids
        airport_id = places[0].place_id
        return populartimes.get_id(API_KEY, airport_id)["populartimes"]


if __name__ == '__main__':
    airports = list(load_airports())
    for airport in airports:
        print(get_airport_popular_times(airport))
    time.sleep(2)
