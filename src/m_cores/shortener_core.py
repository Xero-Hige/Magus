# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

import pickle as Serializer

from core_utils.debugger import debug_core_print_d
from libs.rabbit_handler import *

REP_SIZE = 3


def shorten_repetitions(text):
    """ """
    if not text or len(text) <= REP_SIZE:
        return text

    acum = []
    left = 0
    right = REP_SIZE

    while right < len(text):
        pivot = right

        while pivot > left and text[pivot] == text[right] and pivot > 0:
            pivot -= 1

        if pivot != left:
            while left <= pivot:
                acum.append(text[left])
                left += 1
                right += 1

            continue

        for _ in range(REP_SIZE):
            acum.append(text[pivot])

        left = right

        while left < len(text) and text[pivot] == text[left]:
            left += 1

        right = left + REP_SIZE

    return "".join(acum)


def main(tag, worker_number, input_queue, output_queue):
    reader = RabbitHandler(input_queue)
    writer = RabbitHandler(output_queue)

    def callback(tweet_string):
        if not tweet_string:
            return

        tweet = Serializer.loads(tweet_string)

        if not tweet:
            return

        debug_core_print_d(tag, worker_number, "Shortening tweet")

        tweet['tweet_text'] = shorten_repetitions(tweet['tweet_text'])

        writer.send_message(Serializer.dumps(tweet))

    reader.receive_messages(callback)


if __name__ == '__main__':
    main()
