# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

from m_cores.magus_core import MagusCore

REP_SIZE = 3


class HashtagSplitterCore(MagusCore):
    def __init__(self, input_queue, output_queue, tag="Hashtag Splitter", worker_number=0):
        MagusCore.__init__(self, tag, worker_number, input_queue, output_queue)

    def run_core(self):
        def callback(tweet_string):
            if not tweet_string:
                return

            tweet = self.serializer.loads(tweet_string)

            if not tweet:
                self._log("Can't deserialize tweet")
                return

            i = 0

            if len(tweet["tweet_hashtags"]) == 0:
                self.out_queue.send_message(self.serializer.dumps(tweet))
                return

            words = []
            self._log("Parsing Hashtags")
            for htag in tweet["tweet_hashtags"]:
                while htag not in tweet["words"][i]:
                    words.append(tweet["words"][i])
                    i += 1

                htag_parsed = split_htag(htag)

                word = tweet["words"][i].replace("#" + htag, " " + htag_parsed + " ")
                for w in word.split():
                    words.append(w)

            tweet["words"] = words
            self._log("Hashtags parsed")

            self.out_queue.send_message(self.serializer.dumps(tweet))

        self.in_queue.receive_messages(callback)


def split_htag(htag):
    if len(htag) < 2:
        return htag

    splitted_htag = []

    for i in range(1, len(htag) - 1):
        if htag[i].islower() and not htag[i - 1].islower():
            splitted_htag.append(" ")
        splitted_htag.append(htag[i - 1])

    splitted_htag.append(htag[-1])

    return "".join(splitted_htag)
