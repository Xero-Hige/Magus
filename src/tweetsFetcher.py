#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

from __future__ import absolute_import, print_function, unicode_literals
from twitter import *
from KafkaBroker import KafkaWriter

class TweetsFetcher():

    def __init__(self):
        self.CONSUMER_KEY = ""
        self.CONSUMER_SECRET = ""
        self.TOKEN_KEY = ""
        self.TOKEN_SECRET = ""

        self.get_keys()

        self.auth = OAuth(self.TOKEN_KEY, self.TOKEN_SECRET, self.CONSUMER_KEY, self.CONSUMER_SECRET)

        self.generate_tweet_pool()

    def generate_tweet_pool(self):
        twitter_stream = TwitterStream(auth=self.auth)

        self.tweets = twitter_stream.statuses.filter(locations="-180.0,-90.0, 180.0, 90.0")

    def get_keys(self):
        with open("keys.rsa", "r") as f:
            self.CONSUMER_KEY = f.readline().rstrip('\n')
            self.CONSUMER_SECRET = f.readline().rstrip('\n')
            self.TOKEN_KEY = f.readline().rstrip('\n')
            self.TOKEN_SECRET = f.readline().rstrip('\n')

    def next(self):
        self.__next__()

    def __next__(self):
        while True:
            try:
                return next(self.tweets)

            except Exception as e:
                raise e #FIXME
                self.generate_tweet_pool()

    def __iter__(self):
        return self

def main():
    tf = TweetsFetcher()
    writer = KafkaWriter(b'tweetsInput')

    for t in tf:
        writer.write(t)


if __name__ == '__main__':
    main()