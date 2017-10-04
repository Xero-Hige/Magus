# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

import pickle as Serializer

from core_utils.debugger import debug_core_print_d
from core_utils.rabbit_handler import *
from libs.tweet_anonymize import full_anonymize_tweet

NUMBER_OF_DUMPERS = 1

def main(tag, worker_number, input_queue, output_queue):
    reader = RabbitHandler(input_queue)
    writer = RabbitHandler(output_queue)

    lookup = {}

    def callback(incoming_msg):
        if not incoming_msg:
            return

        msg = Serializer.loads(incoming_msg)

        if not msg:
            return

        tweet_id,dumper = msg

        if tweet_id not in
            lookup[tweet_id] = {dumper:True}
            return

        lookup[tweet_id][dumper] = True

        if len (lookup[tweet_id]) < NUMBER_OF_DUMPERS:
            return

        lookup.pop(tweet_id)
        writer.send_message(Serializer.dumps(tweet_id))

        debug_core_print_d(tag, worker_number, "Emited {}".format(tweet_id))


    reader.receive_messages(callback)


if __name__ == '__main__':
    main()
