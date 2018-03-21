import pickle

import numpy as np

from morgana_cnn_schema import MorganaCNNSchema
from morgana_config_handler import TRAIN_DATA_FOLDER

SEED = 97
SLICE = 50


def get_train_data():
    print("Loading data...")
    x_text, y = MorganaCNNSchema.get_input_data()

    x = x_text

    np.random.seed(SEED)
    shuffle_indices = np.random.permutation(np.arange(len(y)))
    x_shuffled = x[shuffle_indices]
    y_shuffled = y[shuffle_indices]

    dev_sample_index = -1 * int(.11 * float(len(y)))
    x_train, x_dev = x_shuffled[:dev_sample_index], x_shuffled[dev_sample_index:]
    y_train, y_dev = y_shuffled[:dev_sample_index], y_shuffled[dev_sample_index:]

    print("Train/Dev split: {:d}/{:d}".format(len(x_train), len(x_dev)))
    return x_train, y_train, x_dev, y_dev


def main():
    x_data, y_data, dev_x, dev_y = get_train_data()

    i = 0
    while i * SLICE < len(x_data):
        print("SLICE {}".format(i))
        batch = x_data[(i * SLICE):((i + 1) * SLICE)]
        a, b, c = MorganaCNNSchema.map_batch(batch)

        dump = a, b, c, y_data[(i * SLICE):((i + 1) * SLICE)]

        with open("{}/train_batch_{}.dmp".format(TRAIN_DATA_FOLDER, i), 'wb') as output:
            pickle.dump(dump, output)

        i += 1

    i = 0
    while i * SLICE < len(dev_x):
        print("SLICE {}".format(i))
        batch = dev_x[(i * SLICE):((i + 1) * SLICE)]
        a, b, c = MorganaCNNSchema.map_batch(batch)

        dump = a, b, c, dev_y[(i * SLICE):((i + 1) * SLICE)]

        with open("{}/test_batch_{}.dmp".format(TRAIN_DATA_FOLDER, i), 'wb') as output:
            pickle.dump(dump, output)

        i += 1


if __name__ == '__main__':
    main()
