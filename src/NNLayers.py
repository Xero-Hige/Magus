#  Copyright 2016 The TensorFlow Authors. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
"""Convolutional Neural Network Estimator for MNIST, built with tf.layers."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from random import random

import numpy as np
import tensorflow as tf

from libs.db_tweet import DB_Handler
from libs.tweet_parser import TweetParser

tf.logging.set_verbosity(tf.logging.INFO)

ROWS = 70
COLUMNS = 300
TRAIN_STEPS = 20000


def cnn_model_creation(features, labels, mode):
    """Model function for CNN."""
    input_layer = tf.reshape(features["x"], [-1, COLUMNS, ROWS, 1])

    padding = 'same'
    output_width = 3

    conv = get_convolutional_layer(input_layer, output_width, padding)

    flatten = tf.reshape(conv, [-1, 3 * 4 * 16])

    dense = tf.layers.dense(inputs=flatten, units=100, activation=tf.nn.relu)

    dropout = tf.layers.dropout(
            inputs=dense, rate=0.5, training=mode == tf.estimator.ModeKeys.TRAIN)

    logits = tf.layers.dense(inputs=dropout, units=10)

    predictions = {
        # Generate predictions (for PREDICT and EVAL mode)
        "classes": tf.argmax(input=logits, axis=1),
        # Add `softmax_tensor` to the graph. It is used for PREDICT and by the
        # `logging_hook`.
        "probabilities": tf.nn.sigmoid(logits, name="softmax_tensor")
    }

    print(logits)

    if mode == tf.estimator.ModeKeys.PREDICT:
        return tf.estimator.EstimatorSpec(mode=mode, predictions=predictions)

    # Calculate Loss (for both TRAIN and EVAL modes)
    # onehot_labels = tf.one_hot(indices=tf.cast(labels, tf.int32), depth=10)
    print(logits)
    print(labels)
    loss = tf.losses.absolute_difference(labels, logits)
    # .softmax_cross_entropy(
    #       onehot_labels=labels, logits=logits)

    # Configure the Training Op (for TRAIN mode)
    if mode == tf.estimator.ModeKeys.TRAIN:
        optimizer = tf.train.AdadeltaOptimizer()
        train_op = optimizer.minimize(
                loss=loss,
                global_step=tf.train.get_global_step())
        return tf.estimator.EstimatorSpec(mode=mode, loss=loss, train_op=train_op)

    # Add evaluation metrics (for EVAL mode)
    eval_metric_ops = {
        "accuracy": tf.metrics.accuracy(
                labels=tf.argmax(labels, 1), predictions=tf.argmax(logits, 1))}
    return tf.estimator.EstimatorSpec(
            mode=mode, loss=loss, eval_metric_ops=eval_metric_ops)


def get_convolutional_layer(input_layer, output_width, padding):
    filters = []
    filters.append(create_filter_layer(16, input_layer, 2, output_width, padding, 2))
    filters.append(create_filter_layer(16, input_layer, 3, output_width, padding, 3))
    filters.append(create_filter_layer(16, input_layer, 5, output_width, padding, 2))
    filters.append(create_filter_layer(16, input_layer, 7, output_width, padding, 3))
    print(filters)
    conv = tf.concat(filters, 2)

    return conv


def create_filter_layer(kernel_filters, input_layer, kernel_height, output_width, padding, stride_step, name=""):
    conv_filter = tf.layers.conv2d(
            inputs=input_layer,
            filters=kernel_filters,
            kernel_size=[COLUMNS // output_width, kernel_height],
            activation=tf.nn.tanh,
            strides=(COLUMNS // output_width, stride_step),
            padding=padding)  # TODO: add padding
    print(conv_filter)
    max_pool = tf.layers.max_pooling2d(inputs=conv_filter,
                                       pool_size=[1, ROWS // stride_step],
                                       strides=[1, ROWS // stride_step])

    return max_pool


def main(_):
    # Load training and eval data

    eval_data, eval_labels, train_data, train_labels = get_input_data()

    # Create the Estimator
    mnist_classifier = tf.estimator.Estimator(
            model_fn=cnn_model_creation,
            model_dir="/tmp/{}".format(random()))

    train_model(mnist_classifier, train_data, train_labels)

    eval_results = eval_model(train_data, train_labels, mnist_classifier)
    print(eval_results)
    input("--->")
    predict_input_fn = tf.estimator.inputs.numpy_input_fn(
            x={"x": train_data},
            num_epochs=1,
            shuffle=False)
    predictions = mnist_classifier.predict(input_fn=predict_input_fn)
    for i, p in enumerate(predictions):
        print("Prediction %s: %s" % (i + 1, p))


def eval_model(eval_data, eval_labels, mnist_classifier):
    """Evaluates the model and returns the results as string"""
    eval_input_fn = tf.estimator.inputs.numpy_input_fn(
            x={"x": eval_data},
            y=eval_labels,
            num_epochs=25,
            shuffle=False)
    eval_results = mnist_classifier.evaluate(input_fn=eval_input_fn)
    return eval_results


def train_model(model, train_data, train_labels):
    """Trains the model"""
    train_input_fn = tf.estimator.inputs.numpy_input_fn(
            x={"x": train_data},
            y=train_labels,
            batch_size=1,
            num_epochs=2500,
            shuffle=True)
    model.train(
            input_fn=train_input_fn,
            steps=TRAIN_STEPS)


def get_input_data():
    # word_vectors = KeyedVectors.load('./mymodel.mdl')
    missing = []
    with DB_Handler() as handler:
        tagged_tweets = handler.get_all_tagged()

        for tweet_data in tagged_tweets:
            try:
                tweet = TweetParser.parse_from_json_file("../bulk/{}.json".format(tweet_data.id))
            except IOError:
                try:
                    tweet = TweetParser.parse_from_json_file("../tweets/{}.json".format(tweet_data.id))
                except IOError:
                    missing.append(tweet_data.id)
                    continue

            print("[", tweet_data.get_tweet_sentiment(), "] ", tweet[TweetParser.TWEET_TEXT])
            print("( https://magus-catalog.herokuapp.com/classify/{} )".format(tweet_data.id))

    for missi in missing:
        print(missi)
    input()

    words = ["macri", "gato", "cris", "externocleidomastoideo"]
    vectors = []
    for word in words:
        vectors.append(get_word_vector(word, word_vectors))

    while len(vectors) < ROWS:
        vectors.append(np.asarray([0] * COLUMNS))

    vectors = np.append([], vectors)

    print(len(vectors))

    train_data = np.asarray([vectors, vectors, vectors], dtype=np.float32)
    train_data = np.asarray([[0] * (ROWS * COLUMNS), [1] * (ROWS * COLUMNS), [2] * (ROWS * COLUMNS)], dtype=np.float32)

    train_labels = np.asarray([[1 / 10] * 10] + [[2 / 10] * 10] + [[3 / 10] * 10], dtype=np.int32)
    eval_data = np.asarray([[1] * (ROWS * COLUMNS), [2] * (ROWS * COLUMNS)], dtype=np.float32)
    eval_labels = np.asarray([1, 4], dtype=np.int32)
    return eval_data, eval_labels, train_data, train_labels


def get_word_vector(word, word_vectors):
    if word in word_vectors:
        word_vector = word_vectors[word]
    else:
        word_vector = np.asarray([0] * COLUMNS)
    return word_vector


if __name__ == "__main__":
    tf.app.run()
