from __future__ import absolute_import, print_function, unicode_literals

import csv
import os

from twitter import *

WHOLE_WORLD_CORDINATES = "-180.0,-90.0, 180.0, 90.0"


class TweetsFetcher():
    def __init__(self, locations=[], topics=[], geo=""):
        self.CONSUMER_KEY = ""
        self.CONSUMER_SECRET = ""
        self.TOKEN_KEY = ""
        self.TOKEN_SECRET = ""

        self.locations = locations
        self.topics = topics
        self.geo = geo

        self.get_keys()

        self.auth = OAuth(self.TOKEN_KEY, self.TOKEN_SECRET, self.CONSUMER_KEY, self.CONSUMER_SECRET)

        self.tweet_stream = None
        self.generate_tweet_pool()

    def generate_tweet_pool(self):
        twitter_stream = TwitterStream(auth=self.auth)

        location_string = self.get_location_string()

        if self.topics and location_string:
            self.tweet_stream = twitter_stream.statuses.filter(locations=location_string, track=self.topics)
        elif self.topics and not location_string:
            self.tweet_stream = twitter_stream.statuses.filter(track=self.topics)
        else:
            self.tweet_stream = twitter_stream.statuses.filter(locations=WHOLE_WORLD_CORDINATES)

    def get_location_string(self):
        boundaries = []
        if self.locations:
            boundaries = self.get_boundaries_list(self.locations)
        if self.geo:
            boundaries.append(self.geo)
        location_string = ",".join(boundaries)
        return location_string

    @staticmethod
    def get_boundaries_list(locations):
        bounds = []
        with open("./libs/country_bounds.csv", 'r') as _file:
            reader = csv.DictReader(_file)

            for country in reader:

                print(country["country"].lower(), locations, country["country"].lower() in locations)

                if not country["country"].lower() in locations:
                    continue

                geo = "{},{},{},{}".format(country["longmin"],
                                           country["latmin"],
                                           country["longmax"],
                                           country["latmax"])

                bounds.append(geo)

        return bounds

    def get_keys(self):
        self.CONSUMER_KEY = os.environ.get('CONSUMER_KEY', None)
        self.CONSUMER_SECRET = os.environ.get('CONSUMER_SECRET', None)
        self.TOKEN_KEY = os.environ.get('TOKEN_KEY', None)
        self.TOKEN_SECRET = os.environ.get('TOKEN_SECRET', None)

        if self.CONSUMER_KEY:
            return

        with open("src/keys.rsa", "r") as f:
            self.CONSUMER_KEY = f.readline().rstrip('\n')
            self.CONSUMER_SECRET = f.readline().rstrip('\n')
            self.TOKEN_KEY = f.readline().rstrip('\n')
            self.TOKEN_SECRET = f.readline().rstrip('\n')

    def next(self):
        self.__next__()

    def __next__(self):
        while True:
            try:
                return next(self.tweet_stream)

            except Exception as e:
                raise e  # FIXME
                self.generate_tweet_pool()

    def __iter__(self):
        return self
