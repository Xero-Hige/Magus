# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

import pickle as Serializer

from core_utils.debugger import debug_core_print_d
from libs.tweet_anonymize import full_anonymize_tweet
from to_check.RabbitHandler import *


def main(tag, worker_number, input_queue, output_queue):
    reader = RabbitHandler(input_queue)
    writer = RabbitHandler(output_queue)

    def callback(tweet_string):
        if not tweet_string:
            return

        tweet = Serializer.loads(tweet_string)

        if not tweet:
            return

        debug_core_print_d(tag, worker_number, "Cleaning tweet")

        tweet['tweet_text'] = full_anonymize_tweet(tweet['tweet_text'])

        writer.send_message(Serializer.dumps(tweet))

    reader.receive_messages(callback)


if __name__ == '__main__':
    main()
