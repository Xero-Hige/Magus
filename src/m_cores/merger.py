# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

import pickle as Serializer

from core_utils.debugger import debug_core_print_d
from libs.rabbit_handler import *

NUMBER_OF_DUMPERS = 1


def main(tag, worker_number, input_queue, output_queue):
    reader = RabbitHandler(input_queue)
    writer = RabbitHandler(output_queue)

    lookup = {}

    def callback(serialized_advice):
        if not serialized_advice:
            return

        advice = Serializer.loads(serialized_advice)

        if not advice:
            return

        tweet_id = advice["ID"]
        dumper = advice["MatrixFile"]

        if tweet_id not in lookup:
            lookup[tweet_id] = {dumper: True}
            return

        lookup[tweet_id][dumper] = True

        if len(lookup[tweet_id]) < NUMBER_OF_DUMPERS:
            return

        lookup.pop(tweet_id)
        advice.pop("MatrixFile")
        writer.send_message(Serializer.dumps(advice))

        debug_core_print_d(tag, worker_number, "Emited {}".format(tweet_id))

    reader.receive_messages(callback)


if __name__ == '__main__':
    main()
