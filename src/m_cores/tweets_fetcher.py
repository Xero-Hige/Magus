#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

import pickle as Serializer
import sys

from libs.tweet_fetcher import TweetsFetcher
from to_check.RabbitHandler import *


def main(argv=[]):
    tweets_stream = TweetsFetcher()
    handler = RabbitHandler("tweets_input")

    for tweet in tweets_stream:
        handler.send_message(Serializer.dumps(tweet))

    handler.close()


if __name__ == '__main__':
    main(sys.argv)
