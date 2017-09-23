#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

import os
import signal
import time

from to_check.RabbitHandler import *


def main(tag="", worker_number=0, input_queue="", output_queue="tweets_input"):
    tweets = ["../tweets/{}".format(x) for x in os.listdir("../tweets")] \
             + ["../bulk/{}".format(x) for x in os.listdir("../bulk")]

    handler = RabbitHandler(output_queue)

    i = 0

    def handler(signum, frame):
        handler.close()

    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)

    while True:
        with open(tweets[i % len(tweets)]) as tweet_file:
            handler.send_message(tweet_file.read())

        i += 1
        time.sleep(0.25)


if __name__ == '__main__':
    main()
