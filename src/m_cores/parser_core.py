# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

import pickle as Serializer
import sys

from libs.tweet_parser import TweetParser

from src.to_check.RabbitHandler import *


def main(argv=()):
    reader = RabbitHandler("tweets_input")
    writer = RabbitHandler("parsed_tweets")

    def callback(tweet_string):
        if not tweet_string:
            return

        tweet = TweetParser.parse_from_json_string(tweet_string)

        if not tweet:
            return

        writer.send_message(Serializer.dumps(tweet))

    reader.receive_messages(callback)


if __name__ == '__main__':
    main(sys.argv)
