# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

import pickle as Serializer
from sys import stdout

from libs.tweet_parser import TweetParser
from to_check.RabbitHandler import *


def main(tag="", worker_number=0, input_queue="tweets_input", output_queue="parsed_tweets"):
    reader = RabbitHandler(input_queue)
    writer = RabbitHandler(output_queue)

    def callback(tweet_string):
        if not tweet_string:
            return

        print("[{}::{}] Debug: incoming tweet".format(tag, worker_number))
        stdout.flush()

        tweet_dict = Serializer.loads(tweet_string)

        tweet = TweetParser.parse_from_dict(tweet_dict)

        if not tweet:
            return

        writer.send_message(Serializer.dumps(tweet))

    reader.receive_messages(callback)


if __name__ == '__main__':
    main()
