# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

from libs.tweet_parser import TweetParser
from m_cores.magus_core import MagusCore


class ParserCore(MagusCore):
    def __init__(self, input_queue, output_queue, tag="Fetcher", worker_number=0):
        MagusCore.__init__(self, tag, worker_number, input_queue, output_queue)

    def run_core(self):

        def callback(tweet_string):
            if not tweet_string:
                return

            self._log("Incoming tweet")
            full_tweet = self.serializer.loads(tweet_string)

            tweet = TweetParser.parse_from_dict(full_tweet)
            if not tweet:
                self._log("Can't parse tweet")
                return

            self.out_queue.send_message(self.serializer.dumps(tweet))

        self.in_queue.receive_messages(callback)
