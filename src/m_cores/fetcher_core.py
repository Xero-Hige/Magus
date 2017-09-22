#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

import json as Serializer
import sys

from libs.tweet_fetcher import TweetsFetcher
from to_check.RabbitHandler import *


def main(tag="", worker_number=0, input_queue="", output_queue="tweets_input"):
    tweets_stream = TweetsFetcher()
    handler = RabbitHandler(output_queue)

    for tweet in tweets_stream:
        handler.send_message(Serializer.dumps(tweet))

    handler.close()


if __name__ == '__main__':
    main(sys.argv)
