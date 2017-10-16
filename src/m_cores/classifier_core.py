# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

import csv
import pickle as Serializer

from libs.neural_classifier import NeuralClassifier
from libs.rabbit_handler import RabbitHandler
from libs.sentiments_handling import NONE

NUMBER_OF_DUMPERS = 1
DUMPERS_LIST = []


def main(tag, worker_number, input_queue, output_queue):
    reader = RabbitHandler(input_queue)
    writer = RabbitHandler(output_queue)

    classifier = NeuralClassifier()

    def callback(incoming_msg):
        if not incoming_msg:
            return

        tweet = Serializer.loads(incoming_msg)

        if not tweet:
            return

        tweet_id = tweet["tweet_id"]
        latitude = tweet["latitude"]
        longitude = tweet["longitude"]

        matrix = []

        for dumper in sorted(DUMPERS_LIST):
            # TODO: Migrate to a nonsql db
            file_path = "/vectors/{}_{}.csv".format(dumper, tweet_id)

            with open(file_path) as _file:
                csv_reader = csv.reader(_file)
                for line in csv_reader:
                    matrix.append([float(x) for x in line])

                    # TODO: Delete after read

        prediction = classifier.classify(matrix)

        if prediction == NONE:
            return

        writer.send_message(Serializer.dumps(((latitude, longitude), prediction)))

    reader.receive_messages(callback)


if __name__ == '__main__':
    main()
