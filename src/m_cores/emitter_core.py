# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

from m_cores.magus_core import MagusCore


class EmitterCore(MagusCore):
    def __init__(self, input_queue, output_queue, tag="Parser", worker_number=0):
        MagusCore.__init__(self, tag, worker_number, input_queue, output_queue)

    def run_core(self):

        def callback(tweet_string):
            if not tweet_string:
                return

            tweet_info = self.serializer.loads(tweet_string)

            if not tweet_info:
                return

            latitude, longitude = tweet_info["tweet_lat"], tweet_info["tweet_lon"]
            classification = tweet_info["classification"]
            coordinates = (latitude, longitude)
            message = (coordinates, classification)

            self._log("Sent {}".format(message))

            self.out_queue.send_message(self.serializer.dumps(message))

        self.in_queue.receive_messages(callback)
