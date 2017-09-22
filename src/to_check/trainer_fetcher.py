#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

import json
import os
import pickle as Serializer
import sys

from RabbitHandler import *


def main(argv):
    worker = argv[2] if len(argv) > 2 else 0
    debug = worker != 0

    handler = RabbitHandler("tweets_input")
    files = [os.path.join("/training", f) for f in os.listdir("/training") if
             os.path.isfile(os.path.join("/training", f))]

    for f in files:
        if debug:
            print("Worker [", worker, "] ", tweet["preprocessed_text"])
            sys.stdout.flush()

        with open(f) as tweet:
            handler.send_message(Serializer.dumps(json.loads(tweet.read())))

    handler.close()


if __name__ == '__main__':
    main(sys.argv)
