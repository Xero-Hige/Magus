# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

import numpy

from libs.embeddings_handler import EmbeddingHandler
from libs.tweet_parser import TweetParser
from m_cores.magus_dump_core import MagusDumpCore


class RCharsEmbeddingCore(MagusDumpCore):
    def __init__(self, input_queue, output_queue, tag="Rchars Embedding", worker_number=0):
        MagusDumpCore.__init__(self, input_queue, output_queue, tag, worker_number)
        self.embeddings = EmbeddingHandler("rCharsEmbeddings", 150, 320)

    def run_core(self):
        def callback(tweet_string):
            if not tweet_string:
                return

            tweet = self.serializer.loads(tweet_string)
            if not tweet:
                self._log("Can't deserialize tweet")
                return
            self.out_queue.send_message(tweet_string)

            matrix = self.embeddings.get_embedding_matrix(tweet["chars"])

            matrix_filename = "vectors/rchar_matrix_{}.npy".format(tweet[TweetParser.TWEET_ID])
            with open(matrix_filename, 'wb') as matrix_file:
                numpy.save(matrix_file, matrix, allow_pickle=True, fix_imports=True)

            send_advice = (tweet[TweetParser.TWEET_ID], matrix_filename)
            self.dump_queue.send_message(self.serializer.dumps(send_advice))

        self.in_queue.receive_messages(callback)
