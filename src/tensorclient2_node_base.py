# Copyright 2016 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

# !/usr/bin/env python2.7

"""Send JPEG image to tensorflow_model_server loaded with inception model.
"""

from __future__ import print_function

import random

import tensorflow as tf
# This is a placeholder for a Google-internal import.
from grpc.beta import implementations
from tensorflow.python.framework import tensor_util
from tensorflow_serving.apis import predict_pb2, prediction_service_pb2

from libs.sentiments_handling import ANGER, ANTICIPATION, DISGUST, FEAR, JOY, NEUTRAL, SADNESS, SURPRISE, TRUST

EMOTION_LOOKUP = [JOY, TRUST, FEAR, SURPRISE, SADNESS, DISGUST, ANGER, ANTICIPATION, NEUTRAL]

tf.app.flags.DEFINE_string('server', 'localhost:9000',
                           'PredictionService host:port')
tf.app.flags.DEFINE_string('image', '', 'path to image in JPEG format')
FLAGS = tf.app.flags.FLAGS


def main(_):
    host, port = FLAGS.server.split(':')
    channel = implementations.insecure_channel(host, int(port))
    stub = prediction_service_pb2.beta_create_PredictionService_stub(channel)
    # Send request
    # See prediction_service.proto for gRPC request/response details.
    request = predict_pb2.PredictRequest()
    request.model_spec.name = 'morgana'
    request.model_spec.signature_name = 'predict_tweets'

    # x_text, y = AttardiCNNSchema.get_input_data()

    request.inputs['tweet_features'].CopyFrom(
            tf.contrib.util.make_tensor_proto([[random.random() for _ in range(80)] for _ in range(300)],
                                              shape=[1, 80, 300, 1]))
    result = stub.Predict(request, 10.0)  # 10 secs timeout
    result = tensor_util.MakeNdarray(result.outputs["scores"])[0]
    for i in range(len(result)):
        print(EMOTION_LOOKUP[i], ":", result[i])


if __name__ == '__main__':
    tf.app.run()
