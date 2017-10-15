#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

import json
import os
import pickle as Serializer
import signal

from core_utils.debugger import debug_core_print_d
from libs.rabbit_handler import *


def main(tag="", worker_number=0, input_queue="", output_queue="tweets_input"):
    tweets = ["/training/{}".format(x) for x in os.listdir("/training")]  # \
    #           + ["../bulk/{}".format(x) for x in os.listdir("../bulk")]

    handler = RabbitHandler(output_queue)

    i = 0

    def signal_handler(signum, frame):
        handler.close()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    while True:
        with open(tweets[i % len(tweets)]) as tweet_file:
            tweet_dict = json.loads(tweet_file.read())
            handler.send_message(Serializer.dumps(tweet_dict))

        debug_core_print_d(tag, worker_number, "sent {} via {}".format(tweets[i % len(tweets)], output_queue))


if __name__ == '__main__':
    main()
