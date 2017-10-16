# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

from libs.tweet_anonymize import full_anonymize_tweet
from m_cores.magus_core import MagusCore


class AnonymizeCore(MagusCore):
    def __init__(self, input_queue, output_queue, tag="Fetcher", worker_number=0):
        MagusCore.__init__(self, tag, worker_number, input_queue, output_queue)

    def run_core(self):
        def callback(tweet_string):
            if not tweet_string:
                return

            tweet = self.serializer.loads(tweet_string)

            if not tweet:
                self._log("Can't deserialize tweet")
                return

            self._log("Cleaning tweet")
            tweet['tweet_text'] = full_anonymize_tweet(tweet['tweet_text'])
            self._log("Cleaned tweet")

            self.out_queue.send_message(self.serializer.dumps(tweet))

        self.in_queue.receive_messages(callback)
