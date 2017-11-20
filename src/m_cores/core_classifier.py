#!/usr/bin/python
# encoding=utf8

from __future__ import absolute_import, print_function, print_function, unicode_literals

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
                           'morgana:9000',
                           'PredictionService host:port')
FLAGS = tf.app.flags.FLAGS


class ClassifierCore(MagusCore):
    def __init__(self, input_queue, output_queue, tag="Classifier", worker_number=0):
        MagusCore.__init__(self, tag, worker_number, input_queue, output_queue)

        host, port = FLAGS.server.split(':')
        channel = implementations.insecure_channel(host, int(port))
        self.stub = prediction_service_pb2.beta_create_PredictionService_stub(channel)

    def run_core(self):
        def callback(tweet_string):
            if not tweet_string:
                return

            tweet = self.serializer.loads(tweet_string, encoding="latin1")

            if not tweet:
                self._log("Can't deserialize tweet")
                return

            self._log("Classify tweet")
            features_map = self.load_features_map(tweet[TweetParser.TWEET_ID])
            result = self.make_request(features_map)
            self._log("Lowered tweet")

            tweet_info = {"classification":          result,
                          TweetParser.TWEET_ID: tweet[TweetParser.TWEET_ID],
                          "tweet_lat": tweet         ["latitude"],
                          "tweet_lon": tweet         ["longitude"]
                          }

            self.out_queue.send_message(self.serializer.dumps(tweet_info))

        self.in_queue.receive_messages(callback)

    def load_features_map(self, tweet_id):
        return [[0.1 for _ in range(80)] for _ in range(300)]

    def make_request(self, features_map):
        request = predict_pb2.PredictRequest()
        request.model_spec.name = 'morgana'
        request.model_spec.signature_name = 'predict_tweets'

        request.inputs['tweet_features'].CopyFrom(
                tf.contrib.util.make_tensor_proto(features_map,
                                                  shape=[1, 80, 300, 1]))

        result = self.stub.Predict(request, 1)  # 1 secs timeout
        result = int(tensor_util.MakeNdarray(result.outputs["predictions"])[0][0])
        return result
