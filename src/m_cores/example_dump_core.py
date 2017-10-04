# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

import pickle as Serializer

from core_utils.debugger import debug_core_print_d
from core_utils.rabbit_handler import *


def main(tag, worker_number, input_queue, output_queue):
    reader = RabbitHandler(input_queue)
    writer = RabbitHandler(output_queue)

    def callback(tweet_string):
        if not tweet_string:
            return

        tweet = Serializer.loads(tweet_string)

        if not tweet:
            return

        writer.send_message(tweet_string)

        debug_core_print_d(tag, worker_number, "Shortening tweet")

        word_embedings = {w.lower(): [1 if str(unichr(x)) in w else 0 for x in range(256)] for w in
                          tweet["tweet_text"].split() if w}

        embeding = [word_embedings.get(w, [0] * 256) w in tweet["tweet_text"].split()]

        with open("/embedings/EXMPL_{}.csv".format(tweet["tweet_id"]), 'w') as _file:
            csv_writer = csv.writer(_file)
            csv_writer.writerows(embeding)

        writer.send_message(Serializer.dumps(tweet))

    reader.receive_messages(callback)


if __name__ == '__main__':
    main()
