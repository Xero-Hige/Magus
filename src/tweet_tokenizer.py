#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

import os
import pickle as Serializer
import sys

from modules_manager import ModulesManager

from RabbitHandler import *

STOP_LISTS = ["arabic", "chinese", "english", "german", "japanese", "portugese", "spanish"]


def get_tokenizers(excluded=[]):
    lst = os.listdir("tokenizers")

    modules = []

    for x in lst:
        x = x.replace(".py", "")
        x = "tokenizers." + x
        modules.append(__import__(x, fromlist=['']))

    return [module for module in modules if "__" not in module.__name__ and module.__name__ not in excluded]


TOKENIZERS = ModulesManager.get_tokenizers()


def main(argv):
    debug = False
    worker = 0
    if len(argv) > 1:
        debug = True
        worker = argv[1]

    reader = RabbitHandler("fully-preprocessed_tweets")
    writer = RabbitHandler("features_dicts")

    def callback(tweet):

        if not tweet:
            return

        tweet = Serializer.loads(tweet)
        tag = tweet.get("preprocessed_text", None)

        if not tag:  # FIXME remove testing
            return

        tokens = {}
        words = {}
        for tokenizer in TOKENIZERS:
            dict = tokenizer.tokenize(tweet)

            if tokenizer.__name__ == "tokenizers.tokenizer_words":
                words = dict

            for token in dict:
                if token in tokens:
                    continue
                tokens[token] = dict[token]

        if len(words) < 1:
            return


    reader.receive_messages(callback)


if __name__ == '__main__':
    main(sys.argv)
