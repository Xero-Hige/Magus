# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

from m_cores.magus_core import MagusCore


class JoinerCore(MagusCore):
    def __init__(self, input_queue, output_queue, tag="Joiner", worker_number=0):
        MagusCore.__init__(self, tag, worker_number, input_queue, output_queue)
        self.accumulator = {}

    def run_core(self):

        def callback(info_string):
            if not info_string:
                return

            advice = self.serializer.loads(info_string)

            if not advice:
                return

            tweet_id = advice["ID"]
            matrix_filename = advice["MatrixFile"]

            id_accumulator = self.accumulator.get(tweet_id, {})
            id_accumulator[matrix_filename] = None

            if len(id_accumulator) == 3:
                self.accumulator.pop(tweet_id)
                advice.pop("MatrixFile")
                self.out_queue.send_message(self.serializer.dumps(advice))

                self._log("Joined {}".format(tweet_id))
                return

            self.accumulator[tweet_id] = id_accumulator

        self.in_queue.receive_messages(callback)
