# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

import csv
import pickle as Serializer

from core_utils.debugger import debug_core_print_d
from core_utils.rabbit_handler import *

from gensim.models.keyedvectors import KeyedVectors

VECTORS_MODEL_FILE = "/models/base_model.w2v"
OUTPUT_VECTOR_FOLDER = "/vectors/"

JOINER_QUEUE = "joiner_notify"

W2V_VECTORS_LENGHT = 256

DUMPER_TAG = "EXMPL"

def main(tag, worker_number, input_queue, output_queue):
    reader = RabbitHandler(input_queue)
    writer = RabbitHandler(output_queue)
    notifier_writer = RabbitHandler(JOINER_QUEUE)

    model = Word2Vec.load(VECTORS_MODEL_FILE) #TODO: Check if compressing is needed

    def callback(tweet_string):
        if not tweet_string:
            return

        tweet = Serializer.loads(tweet_string)

        if not tweet:
            return

        writer.send_message(tweet_string)

        debug_core_print_d(tag, worker_number, "Getting trained tweets W2V")

        word_embedings = {w.lower(): [1 if str(unichr(x)) in w else 0 for x in range(W2V_VECTORS_LENGHT)] for w in
                          tweet["tweet_text"].split() if w}

        embeding = [word_embedings.get(w, [0] * 256) for w in tweet["tweet_text"].split()]

        with open(OUTPUT_VECTOR_FOLDER + "/EXMPL_{}.csv".format(tweet["tweet_id"]), 'w') as _file:
            csv_writer = csv.writer(_file)
            csv_writer.writerows(embeding)

        notifier_writer.send_message(Serializer.dumps((tweet["tweet_id"],DUMPER_TAG)))

    reader.receive_messages(callback)


if __name__ == '__main__':
    main()
