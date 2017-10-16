# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

import pickle as Serializer

from libs.rabbit_handler import *
from libs.sentiments_handling import HAPPY


def main(tag, worker_number, input_queue, output_queue):
    reader = RabbitHandler(input_queue)
    writer = RabbitHandler(output_queue)

    def callback(tweet_string):
        if not tweet_string:
            return

        tweet = Serializer.loads(tweet_string)

        if not tweet:
            return

        latitude, longitude = tweet["latitude"], tweet["longitude"]

        coordinates = (latitude, longitude)
        message = (coordinates, HAPPY)

        writer.send_message(Serializer.dumps(message))

    reader.receive_messages(callback)


if __name__ == '__main__':
    main()
