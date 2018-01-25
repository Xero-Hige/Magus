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

"""Train and export a simple Softmax Regression TensorFlow model.
The model is from the TensorFlow "MNIST For ML Beginner" tutorial. This program
simply follows all its training instructions, and uses TensorFlow SavedModel to
export the trained model with proper signatures that can be loaded by standard
tensorflow_model_server.
Usage: mnist_export.py [--training_iteration=x] [--model_version=y] export_dir
"""

import os
import pickle
import random
import sys

import numpy as np
import tensorflow as tf
from tensorflow.python.saved_model import builder as saved_model_builder, signature_constants, signature_def_utils, \
    tag_constants, utils
from tensorflow.python.util import compat

# training flags
from morgana_cnn_schema import MAX_WORDS, MorganaCNNSchema

VOCAB_SIZE = MAX_WORDS
EMBEDDINGS_LENGTH = 300
NUM_CLASSES = 9

tf.app.flags.DEFINE_integer('training_iteration', 1000, 'number of training iterations.')
tf.app.flags.DEFINE_integer('model_version', 1, 'version number of the model.')
tf.app.flags.DEFINE_string('work_dir', '/tmp', 'Working directory.')

tf.flags.DEFINE_integer("embedding_dim", 300, "Dimensionality of character embedding (default: 128)")
tf.flags.DEFINE_string("filter_sizes", "7,7,7", "Comma-separated filter sizes (default: '3,4,5')")
tf.flags.DEFINE_integer("num_filters", 200, "Number of filters per filter size (default: 128)")
tf.flags.DEFINE_float("dropout_keep_prob", 0.5, "Dropout keep probability (default: 0.5)")
tf.flags.DEFINE_float("l2_reg_lambda", 0, "L2 regularization lambda (default: 0.0)")

FLAGS = tf.app.flags.FLAGS


def batch_iter(x, y, batch_size, shuffle=True):
    """
    Generates a batch iterator for a dataset.
    """

    data_size = len(x)
    # data = np.array(list(zip(x, y)))
    data = list(zip(x, y))

    num_batches_per_epoch = int((len(x) - 1) / batch_size) + 1

    # Shuffle the data at each epoch
    if shuffle:
        # shuffle_indices = np.random.permutation(np.arange(data_size))
        # shuffled_data = data[shuffle_indices]
        random.shuffle(data)
        shuffled_data = data
    else:
        shuffled_data = data

    for batch_num in range(num_batches_per_epoch):

        start_index = batch_num * batch_size
        end_index = min((batch_num + 1) * batch_size, data_size)

        x_list = []
        y_list = []
        for i in range(start_index, end_index):
            x_list.append(shuffled_data[i][0])
            y_list.append(shuffled_data[i][1])

        x_list = MorganaCNNSchema.map_batch(x_list)

        yield x_list, y_list


def main(_):
    iterations = int(sys.argv[1])
    filters = sys.argv[2]
    n_filters = int(sys.argv[3])
    output_folder = sys.argv[4]
    model_version = int(sys.argv[5])
    start_it = int(sys.argv[6])

    # Train model
    print('Training model...')

    # Read the data and format it

    sess = tf.InteractiveSession()

    # Build model
    # x_train, y_train = get_train_data()

    cnn = MorganaCNNSchema(
            num_classes=9,  # y_train.shape[1],
            vocab_size=VOCAB_SIZE,
            embedding_size=FLAGS.embedding_dim,
            filter_sizes=list(map(int, filters.split(","))),
            num_filters=n_filters,
            l2_reg_lambda=FLAGS.l2_reg_lambda)

    train_step = tf.train.AdamOptimizer(1e-3).minimize(cnn.loss)

    tf.initialize_all_variables().run()

    # train the model
    prediction_classes = 9  # y_train.shape[1]

    saver = tf.train.Saver()

    if start_it != 0:
        saver.restore(sess, "tmp/" + output_folder + "_{}.ckpt".format(start_it))

    test_batches = ["/media/hige/320/train_data/batch_{}.dmp".format(x) for x in range(14)]
    batches = ["/media/hige/320/train_data/batch_{}.dmp".format(x) for x in range(14, 135)]

    for it in range(start_it + 1, iterations):
        do_train_step(batches, cnn, it, output_folder, saver, sess, train_step)

        if it % (3) == 0:
            do_test_step(test_batches, cnn, sess)

    do_test_step(test_batches, cnn, sess)
    print('Done training!')

    # Save the model

    # where to save to?
    export_path_base = output_folder
    export_path = os.path.join(
            compat.as_bytes(export_path_base),
            compat.as_bytes(str(model_version)))

    print('Exporting trained model to', export_path)

    # This creates a SERVABLE from our model
    # saves a "snapshot" of the trained model to reliable storage
    # so that it can be loaded later for inference.
    # can save as many version as necessary

    # the tensoroflow serving main file tensorflow_model_server
    # will create a SOURCE out of it, the source
    # can house state that is shared across multiple servables
    # or versions

    # we can later create a LOADER from it using tf.saved_model.loader.load

    # then the MANAGER decides how to handle its lifecycle

    builder = saved_model_builder.SavedModelBuilder(export_path)

    # Build the signature_def_map.
    # Signature specifies what type of model is being exported,
    # and the input/output tensors to bind to when running inference.
    # think of them as annotiations on the graph for serving
    # we can use them a number of ways
    # grabbing whatever inputs/outputs/models we want either on server
    # or via client
    classification_inputs_words = utils.build_tensor_info(cnn.input_x_words)
    classification_inputs_chars = utils.build_tensor_info(cnn.input_x_chars)
    classification_inputs_rchar = utils.build_tensor_info(cnn.input_x_rchars)
    classification_outputs_classes = utils.build_tensor_info(cnn.input_y)
    classification_outputs_scores = utils.build_tensor_info(cnn.scores)

    classification_signature = signature_def_utils.build_signature_def(
            inputs={"words": classification_inputs_words,
                    "chars": classification_inputs_chars,
                    "rchar": classification_inputs_rchar},
            outputs={
                signature_constants.CLASSIFY_OUTPUT_CLASSES:
                    classification_outputs_classes,
                signature_constants.CLASSIFY_OUTPUT_SCORES:
                    classification_outputs_scores
            },
            method_name=signature_constants.CLASSIFY_METHOD_NAME)

    tensor_info_scores = utils.build_tensor_info(cnn.scores)
    tensor_info_predictions = utils.build_tensor_info(cnn.predictions)

    prediction_signature = signature_def_utils.build_signature_def(
            inputs={"words": classification_inputs_words,
                    "chars": classification_inputs_chars,
                    "rchar": classification_inputs_rchar},
            outputs={'scores': tensor_info_scores, 'predictions': tensor_info_predictions},
            method_name=signature_constants.PREDICT_METHOD_NAME)

    legacy_init_op = tf.group(tf.tables_initializer(), name='legacy_init_op')

    # add the sigs to the servable
    builder.add_meta_graph_and_variables(
            sess, [tag_constants.SERVING],
            signature_def_map={
                'predict_tweets':
                    prediction_signature,
                signature_constants.DEFAULT_SERVING_SIGNATURE_DEF_KEY:
                    classification_signature,
            },
            legacy_init_op=legacy_init_op)

    # save it!
    builder.save()

    print('Done exporting!')


def do_train_step(batches, cnn, it, output_folder, saver, sess, train_step):
    print("Iteration ", it)
    random.shuffle(batches)
    total_loss = 0
    total_accuracy = 0
    total_batches = 0
    for batch_number in range(len(batches)):
        with open(batches[batch_number], 'rb') as pickled:
            batch_data = pickle.load(pickled)

        print("Iteration: {} - Batch: {}/{}".format(it, batch_number + 1, len(batches)))

        _, loss, accuracy = sess.run([train_step, cnn.loss, cnn.accuracy], feed_dict={
            cnn.input_x_words: batch_data [0],
            cnn.input_x_chars: batch_data [1],
            cnn.input_x_rchars: batch_data[2],
            cnn.input_y: batch_data       [3],
            cnn.dropout_keep_prob:        0.5
        })

        total_batches += 1
        total_accuracy += accuracy
        total_loss += loss

        print('\n####b--{}--b#####\nLoss: {}\nAccuracy: {}\n#####--{}--#####'.format(batch_number,
                                                                                     loss,
                                                                                     accuracy,
                                                                                     batch_number)
              )
    print('\n#####--{}--#####\nLoss: {}\nAccuracy: {}\n#####--{}--#####'.format(it,
                                                                                total_loss / total_accuracy,
                                                                                total_accuracy / total_batches,
                                                                                it)
          )
    save_path = saver.save(sess, "tmp/" + output_folder + "_{}.ckpt".format(it))
    print("Iteration training end: {}".format(save_path))


def do_test_step(batches, cnn, sess):
    total_loss = 0
    total_accuracy = 0
    total_batches = 0
    random.shuffle(batches)
    for batch_number in range(len(batches)):
        with open(batches[batch_number], 'rb') as pickled:
            batch_data = pickle.load(pickled)

        print("Test batch: {}/{}".format(batch_number, len(batches)))
        feed_dict = {
            cnn.input_x_words: batch_data [0],
            cnn.input_x_chars: batch_data [1],
            cnn.input_x_rchars: batch_data[2],
            cnn.input_y: batch_data       [3],
            cnn.dropout_keep_prob:        1.0
        }

        loss, accuracy = sess.run([cnn.loss, cnn.accuracy], feed_dict)
        total_batches += 1
        total_accuracy += accuracy
        total_loss += loss
    print('\n#####--{}--#####\nLoss: {}\nAccuracy: {}\n#####--{}--#####'.format("X",
                                                                                total_loss / total_accuracy,
                                                                                total_accuracy / total_batches,
                                                                                "X")
          )


def get_train_data():
    print("Loading data...")
    x_text, y = MorganaCNNSchema.get_input_data()

    x = x_text

    np.random.seed(10)
    shuffle_indices = np.random.permutation(np.arange(len(y)))
    x_shuffled = x[shuffle_indices]
    y_shuffled = y[shuffle_indices]

    # dev_sample_index = -1 * int(FLAGS.dev_sample_percentage * float(len(y)))
    x_train, x_dev = x_shuffled, x_shuffled  # x_shuffled[:dev_sample_index], x_shuffled[dev_sample_index:]
    y_train, y_dev = y_shuffled, y_shuffled  # y_shuffled[:dev_sample_index], y_shuffled[dev_sample_index:]

    print("Vocabulary Size: {:d}".format(70))
    print("Train/Dev split: {:d}/{:d}".format(len(x_train), len(x_dev)))
    return x_train, y_train


if __name__ == '__main__':
    tf.app.run()
