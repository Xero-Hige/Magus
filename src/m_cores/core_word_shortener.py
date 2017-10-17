# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

from m_cores.magus_core import MagusCore

REP_SIZE = 3


class WordShortenerCore(MagusCore):
    def __init__(self, input_queue, output_queue, tag="Word Shortener", worker_number=0):
        MagusCore.__init__(self, tag, worker_number, input_queue, output_queue)

    def run_core(self):
        def callback(tweet_string):
            if not tweet_string:
                return

            tweet = self.serializer.loads(tweet_string)

            if not tweet:
                self._log("Can't deserialize tweet")
                return

            self._log("Splitting tweet")
            for i in range(len(tweet["words"])):
                tweet['words'][i] = word_shorten(tweet['words'][i])
            self._log("Splited tweet")

            self.out_queue.send_message(self.serializer.dumps(tweet))

        self.in_queue.receive_messages(callback)


def word_shorten(word):
    """ """
    if not word or len(word) <= REP_SIZE:
        return word

    acum = []
    left = 0
    right = REP_SIZE

    while right < len(word):
        pivot = right

        while pivot > left and word[pivot] == word[right] and pivot > 0:
            pivot -= 1

        if pivot != left:
            while left <= pivot:
                acum.append(word[left])
                left += 1
                right += 1

            continue

        for _ in range(REP_SIZE):
            acum.append(word[pivot])

        left = right

        while left < len(word) and word[pivot] == word[left]:
            left += 1

        right = left + REP_SIZE

    return "".join(acum)
