#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

from libs.tweet_fetcher import TweetsFetcher
from m_cores.magus_core import MagusCore


class FetcherCore(MagusCore):
    def __init__(self, input_queue, output_queue, tag="Fetcher", worker_number=0):
        MagusCore.__init__(self, tag, worker_number, input_queue, output_queue)
        self.tweets_stream = TweetsFetcher(locations=("Argentina",))

    def run_core(self):
        for tweet in self.tweets_stream:
            self._log("Tweet received")
            self.out_queue.send_message(self.serializer.dumps(tweet))
            self._log("Tweet sent")

        self.out_queue.close()
