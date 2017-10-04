# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

import pickle as Serializer

from core_utils.debugger import debug_core_print_d
from core_utils.rabbit_handler import *
from libs.tweet_anonymize import full_anonymize_tweet

NUMBER_OF_DUMPERS = 1

def main(tag, worker_number, input_queue, output_queue):
    reader = RabbitHandler(input_queue)
    writer = RabbitHandler(output_queue)

    def callback(incoming_msg):
        if not incoming_msg:
            return

        msg = Serializer.loads(incoming_msg)

        if not msg:
            return

        tweet_id = msg

        matrix = []

        for dumper in sorted(DUMPERS_LIST):
            file_path = "/vectors/{}_{}.csv".format(dumper,tweet_id)

            with open(file_path) as _file:
                csv_reader = csv.reader(_file)
                for line in csv_reader:
                    matrix.append( [float(x) for x in line] )


        predictions = classifier.classify(matrix)

        writer.send_message(Serializer.dumps({"tweet_id":tweet_id,"predictions":predictions}))

        debug_core_print_d(tag, worker_number, "Emited prediction{}".format(tweet_id))


    reader.receive_messages(callback)


if __name__ == '__main__':
    main()
