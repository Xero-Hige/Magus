#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, print_function, unicode_literals

import os

import grpc
import numpy
import tensorflow as tf
# This is a placeholder for a Google-internal import.
from grpc.beta import implementations
from tensorflow.python.framework import tensor_util
from tensorflow_serving.apis import predict_pb2, prediction_service_pb2

from libs.sentiments_handling import ANGER, ANTICIPATION, DISGUST, FEAR, JOY, NEUTRAL, SADNESS, SURPRISE, TRUST
from libs.tweet_parser import TweetParser
from m_cores.magus_core import MagusCore

EMOTION_LOOKUP = [JOY, TRUST, FEAR, SURPRISE, SADNESS, DISGUST, ANGER, ANTICIPATION, NEUTRAL]

tf.app.flags.DEFINE_string('server',
                           '172.19.0.1:9000',
                           'PredictionService host:port')
FLAGS = tf.app.flags.FLAGS


class ClassifierCore(MagusCore):
    def __init__(self, input_queue, output_queue, tag="Classifier", worker_number=0):
        MagusCore.__init__(self, tag, worker_number, input_queue, output_queue)

        host, port = os.environ.get('TENSORCLIENT', "0.0.0.0").split(':')
        channel = implementations.insecure_channel(host, int(port))
        self.stub = prediction_service_pb2.beta_create_PredictionService_stub(channel)
        self._log("Started Classifier")

    def run_core(self):
        def callback(tweet_id_string):
            if not tweet_id_string:
                return

            tweet_id = self.serializer.loads(tweet_id_string, encoding="utf-8")

            if not tweet_id:
                self._log("Can't deserialize tweet_id")
                return

            self._log("Classify {}".format(tweet_id))

            rchar_matrix = numpy.load("vectors/rchar_matrix_{}.npy".format(tweet_id), allow_pickle=False,
                                      fix_imports=True)
            char_matrix = numpy.load("vectors/char_matrix_{}.npy".format(tweet_id), allow_pickle=False,
                                     fix_imports=True)
            word_matrix = numpy.load("vectors/word_matrix_{}.npy".format(tweet_id), allow_pickle=False,
                                     fix_imports=True)

            os.remove("vectors/rchar_matrix_{}.npy".format(tweet_id))
            os.remove("vectors/char_matrix_{}.npy".format(tweet_id))
            os.remove("vectors/word_matrix_{}.npy".format(tweet_id))

            self._log("Classify new tweet_id")
            result = self.make_request(rchar_matrix, char_matrix, word_matrix)
            self._log("Classified new tweet_id {} as {}".format(tweet_id, result))

            if result is None:
                return

            tweet_info = {"classification":     result,
                          TweetParser.TWEET_ID: tweet_id,
                          # "tweet_lat": tweet_id         ["latitude"],
                          # "tweet_lon": tweet_id         ["longitude"]
                          }

            self.out_queue.send_message(self.serializer.dumps(tweet_info))
            self._log("Sent {}".format(tweet_id))

        self.in_queue.receive_messages(callback)

    # def load_features_map(self, tweet_id):
    #    return [[0.1 for _ in range(80)] for _ in range(300)]

    def make_request(self, rchar_matrix, char_matrix, word_matrix):
        request = predict_pb2.PredictRequest()
        request.model_spec.name = 'morgana'
        request.model_spec.signature_name = 'predict_tweets'

        request.inputs['rchar'].CopyFrom(
                tf.contrib.util.make_tensor_proto(rchar_matrix,
                                                  shape=[1, 320, 300, 1],
                                                  dtype=tf.float32))
        request.inputs['chars'].CopyFrom(
                tf.contrib.util.make_tensor_proto(char_matrix,
                                                  shape=[1, 320, 300, 1],
                                                  dtype=tf.float32))
        request.inputs['words'].CopyFrom(
                tf.contrib.util.make_tensor_proto(word_matrix,
                                                  shape=[1, 120, 300, 1],
                                                  dtype=tf.float32))
        try:
            result = self.stub.Predict(request, 2)  # 1 secs timeout
        except grpc.framework.interfaces.face.face.ExpirationError as e:
            self._log("Timeout")
            return None

        prediction_index = int(tensor_util.MakeNdarray(result.outputs["predictions"])[0])
        return EMOTION_LOOKUP[prediction_index]
