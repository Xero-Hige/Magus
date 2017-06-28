#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

import json
import os
import pickle as Serializer
from itertools import cycle

from RabbitHandler import *


def main():
    handler = RabbitHandler("tweets_input")
    files = [os.path.join("/training", f) for f in os.listdir("/training") if
             os.path.isfile(os.path.join("/training", f))]

    for f in cycle(files):
        with open(f) as tweet:
            handler.send_message(Serializer.dumps(json.loads(tweet.read())))

    handler.close()


if __name__ == '__main__':
    main()
