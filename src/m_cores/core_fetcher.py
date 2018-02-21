#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

import json
import time

from libs.tweet_fetcher import TweetsFetcher
from m_cores.magus_core import MagusCore


class FetcherCore(MagusCore):
    def __init__(self, input_queue, output_queue, tag="Fetcher", worker_number=0):
        MagusCore.__init__(self, tag, worker_number, input_queue, output_queue)
        self.tweets_stream = TweetsFetcher(langs=["en"])

    def run_core(self):
        for tweet in self.tweets_stream:
            self._log("Tweet received")
            if not "id" in tweet:
                continue
            tweet_string = json.dumps(tweet)
            self.out_queue.send_message(tweet_string)
            with open("/tweets/{}.json".format(tweet["id"]), 'w') as output:
                output.write(tweet_string)
            self._log("Tweet sent")
            time.sleep(0.5)
        self.out_queue.close()
        return 0
