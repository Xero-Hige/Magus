from __future__ import absolute_import, print_function, unicode_literals

import os

from twitter import *

from libs.locations import get_coordinates_from_country

WHOLE_WORLD_CORDINATES = "-180.0,-90.0, 180.0, 90.0"


class TweetsFetcher():
    def __init__(self, locations=(), topics=(), geo=""):
        self.CONSUMER_KEY = ""
        self.CONSUMER_SECRET = ""
        self.TOKEN_KEY = ""
        self.TOKEN_SECRET = ""

        self.locations = locations
        self.topics = ",".join(topics)
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
        elif not self.topics and location_string:
            self.tweet_stream = twitter_stream.statuses.filter(locations=location_string)
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
        for country in locations:
            b_box = get_coordinates_from_country(country)

            if not b_box:
                continue

            W, S, E, N = b_box

            geo = "{},{},{},{}".format(W, S, E, N)

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
