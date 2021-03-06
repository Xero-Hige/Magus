# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

import heapq

from pubnub.exceptions import PubNubException
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub

from m_cores.magus_core import MagusCore


class HtagEmitterCore(MagusCore):
    def __init__(self, input_queue, output_queue, tag="Parser", worker_number=0):
        MagusCore.__init__(self, tag, worker_number, input_queue, output_queue)

        pnconfig = PNConfiguration()
        pnconfig.subscribe_key = "sub-c-1d2d27fc-12bd-11e8-91c1-eac6831c625c"
        pnconfig.publish_key = "pub-c-7a828306-4ddf-425c-80ec-1e4f8763c088"
        pnconfig.ssl = False

        self.pubnub = PubNub(pnconfig)

        self.htags = [{}, {}, {}]
        self.count = 0

    def run_core(self):

        def callback(text):
            if not text:
                return

            self._log("Incoming words tweet {}".format(text))

            for htag in filter(lambda x: x[0] == "#", text.split()):
                self.htags[0][htag] = self.htags[0].get(htag, 0) + 1
                self.htags[1][htag] = self.htags[1].get(htag, 0) + 1
                self.htags[2][htag] = self.htags[2].get(htag, 0) + 1

            self.count += 1

            if self.count % 50 == 0:
                htags = self.htags[0]

                if self.count % 100 == 0:
                    htags = self.htags.pop(0)
                    self.htags.append({})

                top_htags = heapq.nlargest(10, htags, key=htags.get)

                while len(top_htags) < 10:
                    top_htags.append("")

                self._log(str(top_htags))

                try:
                    envelope = self.pubnub.publish().channel("Toptags").message({
                        "status": True,
                        "words": top_htags
                    }).sync()  # TODO: Check
                    self._log("Published timetoken: {}".format(envelope.result.timetoken))
                except PubNubException as e:
                    self._log(str(e))

        self.in_queue.receive_messages(callback)
