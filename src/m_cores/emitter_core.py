# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

from pubnub.exceptions import PubNubException
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub

from m_cores.magus_core import MagusCore


class EmitterCore(MagusCore):
    def __init__(self, input_queue, output_queue, tag="Parser", worker_number=0):
        MagusCore.__init__(self, tag, worker_number, input_queue, output_queue)

        pnconfig = PNConfiguration()
        pnconfig.subscribe_key = "sub-c-1d2d27fc-12bd-11e8-91c1-eac6831c625c"
        pnconfig.publish_key = "pub-c-7a828306-4ddf-425c-80ec-1e4f8763c088"
        pnconfig.ssl = False

        self.pubnub = PubNub(pnconfig)

    def run_core(self):

        def callback(tweet_string):
            if not tweet_string:
                return

            self._log("Incoming emitter tweet {}".format(tweet_string))
            tweet_info = self.serializer.loads(tweet_string)

            if not tweet_info:
                return

            latitude, longitude = tweet_info["tweet_lat"], tweet_info["tweet_lon"]
            classification = tweet_info["classification"]
            text = tweet_info["tweet_text"]
            self._log("Sent {}".format(classification))

            try:
                self.pubnub.publish().channel(classification).message({
                    "status": True,
                    'long': latitude,
                    'lat': longitude,
                    "words": text
                }).sync()  # TODO: Check
                # print("publish timetoken: %d" % envelope.result.timetoken)
            except PubNubException as e:
                print("Error")

            self.out_queue.send_message(self.serializer.dumps(text))

        self.in_queue.receive_messages(callback)
