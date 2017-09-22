#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

import json as Serializer
import os

import tweepy

TWEETS_DIR = "../../gittweets/"


class TweetsDownloader():
    def __init__(self):
        self.CONSUMER_KEY = ""
        self.CONSUMER_SECRET = ""
        self.TOKEN_KEY = ""
        self.TOKEN_SECRET = ""

        self.get_keys()
        auth = tweepy.OAuthHandler(self.CONSUMER_KEY, self.CONSUMER_SECRET)
        auth.set_access_token(self.TOKEN_KEY, self.TOKEN_SECRET)
        self.api = tweepy.API(auth)

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

    def get_tweet(self, t_id):
        return self.api.get_status(t_id)


def __iter__(self):
    return self


def main():
    t_id = input("id: ")
    downloader = TweetsDownloader()
    while t_id:
        if os.path.exists(TWEETS_DIR + t_id + ".json"):
            t_id = input("id: ")
            continue

        try:
            with open(TWEETS_DIR + t_id + ".json", 'w') as t_file:
                tweet = downloader.get_tweet(t_id)
                t_file.write(Serializer.dumps(tweet._json))
        except Exception as e:
            print("Error ", str(e))
        t_id = input("id: ")


if __name__ == '__main__':
    main()
