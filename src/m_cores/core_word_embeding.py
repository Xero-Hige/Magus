# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

import numpy

from libs.embeddings_handler import EmbeddingHandler
from libs.tweet_parser import TweetParser
from m_cores.magus_dump_core import MagusDumpCore


# TODO: RENAME
class WordEmbeddingCore(MagusDumpCore):
    def __init__(self, input_queue, output_queue, tag="Word Embedding", worker_number=0):
        MagusDumpCore.__init__(self, input_queue, output_queue, tag, worker_number)
        self.embeddings = EmbeddingHandler("words_embeddings", 300, 120)

    def run_core(self):
        def callback(tweet_string):
            if not tweet_string:
                return

            tweet = self.serializer.loads(tweet_string)
            if not tweet:
                self._log("Can't deserialize tweet")
                return

            matrix = self.embeddings.get_embedding_matrix(tweet["words"])

            matrix_filename = "vectors/word_matrix_{}.npy".format(tweet[TweetParser.TWEET_ID])
            with open(matrix_filename, 'wb') as matrix_file:
                numpy.save(matrix_file, matrix, allow_pickle=True, fix_imports=True)

            advice = {
                "ID": tweet[TweetParser.TWEET_ID],
                "Latitude": tweet[TweetParser.LATITUDE],
                "Longitude": tweet[TweetParser.LONGITUDE],
                "MatrixFile": matrix_filename,
                "Text": tweet[TweetParser.TWEET_TEXT]
            }
            self.dump_queue.send_message(self.serializer.dumps(advice))

        self.in_queue.receive_messages(callback)
