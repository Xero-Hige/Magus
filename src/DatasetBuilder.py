import pickle

import numpy as np
import tensorflow as tf

from morgana_cnn_schema import MorganaCNNSchema


def _float_feature(value):
    return tf.train.Feature(bytes_list=tf.train.FloatList(value=[value]))


tfrecords_filename = 'tweets.tfrecords'

writer = tf.python_io.TFRecordWriter(tfrecords_filename)


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


x_data, y_data = get_train_data()

SLICE = 50

i = 0
while i * SLICE < len(x_data):
    print("SLICE {}".format(i))
    batch = x_data[(i * SLICE):((i + 1) * SLICE)]
    a, b, c = MorganaCNNSchema.map_batch(batch)

    dump = a, b, c, y_data[(i * SLICE):((i + 1) * SLICE)]

    with open("/media/hige/320/train_data/batch_{}.dmp".format(i), 'wb') as output:
        pickle.dump(dump, output)

    i += 1
