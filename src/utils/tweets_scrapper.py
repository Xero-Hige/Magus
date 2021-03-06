#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

import json as Serializer
import os
import signal

import libs.tweet_fetcher as tweet_fetcher

BULK_FOLDER = "bulk"

MAX_SCRAPPING = 200

SCRAP_TIME = 200


def do_scrapping(locations="", topics="", geo="", folder=BULK_FOLDER, scrap_time=SCRAP_TIME, scrap_count=MAX_SCRAPPING):
    if locations:
        locations = [s.lower() for s in locations.split(",")]
    if topics:
        topics = [s.lower() for s in topics.split(",")]

    streamer = tweet_fetcher.TweetsFetcher(locations=locations,
                                           topics=topics,
                                           geo=geo)

    def stop(signum, frame):
        raise StopIteration

    signal.signal(signal.SIGALRM, stop)
    if scrap_time > 0:
        signal.alarm(SCRAP_TIME)

    count = 0

    try:
        for tweet in streamer:

            if not "id" in tweet:
                continue

            t_id = str(tweet["id"])

            if "retweeted_status" in tweet:
                t_id = str(tweet["retweeted_status"]["id"])

            if os.path.exists("../bulk/" + t_id + ".json"):
                continue

            try:
                with open(folder + "/" + t_id + ".json", 'w') as t_file:
                    t_file.write(Serializer.dumps(tweet))
                count += 1
            except Exception as e:
                print("Error ", str(e))

            if 0 < scrap_count < count:
                break

    except StopIteration:
        print("DEBUG - INFO: Scrapping time out")


if __name__ == '__main__':
    do_scrapping()
