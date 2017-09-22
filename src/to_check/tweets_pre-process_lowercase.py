# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

import pickle as serializer
import sys

from RabbitHandler import *
from modules_manager import ModulesManager

PREPROCESSORS = ModulesManager.get_preprocessors()


def main(argv):
    debug = False
    worker = 0
    if len(argv) > 1:
        debug = True
        worker = argv[1]

    reader = RabbitHandler("raw-preprocessed_tweets")
    writer = RabbitHandler("fully-preprocessed_tweets")

    def callback(tweet):
        if not tweet:
            return

        tweet = serializer.loads(tweet)

        word_list = tweet["text"].lower().split()

        for i, word in enumerate(word_list):
            for preprocessor in PREPROCESSORS:
                word, updated = preprocessor.preprocess(word)
                if updated:
                    word_list[i] = word
                    break

        tweet["preprocessed_text"] = " ".join(word_list)

        if debug:
            print("Worker [", worker, "] ", tweet["preprocessed_text"])
            sys.stdout.flush()

        writer.send_message(serializer.dumps(tweet))

    reader.receive_messages(callback)


if __name__ == '__main__':
    main(sys.argv)
