# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

from libs.tweet_parser import TweetParser
from m_cores.magus_core import MagusCore


class EmitterCore(MagusCore):
    def __init__(self, input_queue, output_queue, tag="Parser", worker_number=0):
        MagusCore.__init__(self, tag, worker_number, input_queue, output_queue)

    def run_core(self):

        def callback(tweet_string):
            if not tweet_string:
                return

            self._log("Incoming emitter tweet {}".format(tweet_string))
            tweet_info = self.serializer.loads(tweet_string)

            if not tweet_info:
                return

            # latitude, longitude = tweet_info["tweet_lat"], tweet_info["tweet_lon"]
            classification = tweet_info["classification"]
            tweet_id = tweet_info[TweetParser.TWEET_ID]

            with open("/output_folder/classification.html", 'a') as output:
                output.write("<a href=\"https://twitter.com/statuses/{}\">{}</a><br>".format(tweet_id, classification))

                # coordinates = (latitude, longitude)
                # message = (coordinates, classification)

                # self._log("Sent {}".format(message))

                #self.out_queue.send_message(self.serializer.dumps(message))

        self.in_queue.receive_messages(callback)
