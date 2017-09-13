#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

import json as Serializer
import time

import libs.tweet_fetcher as tweet_fetcher

MAX_SCRAPPING = 10

SCRAP_TIME = 10


def do_scrapping(locations="", topics="", geo=""):
    locations = [s.lower() for s in locations.split(",")]
    topics = [s.lower() for s in topics.split(",")]

    streamer = tweet_fetcher.TweetsFetcher(locations=locations,
                                           topics=topics,
                                           geo=geo)

    count = 0
    start_time = time.time()

    for tweet in streamer:

        print(tweet)

        if not "id" in tweet:
            continue

        t_id = str(tweet["id"])



        try:
            with open("../bulk/" + t_id + ".json", 'w') as t_file:
                t_file.write(Serializer.dumps(tweet))
            count += 1
        except Exception as e:
            print("Error ", str(e))

        if time.time() - start_time > SCRAP_TIME or count > MAX_SCRAPPING:
            break


if __name__ == '__main__':
    do_scrapping()
