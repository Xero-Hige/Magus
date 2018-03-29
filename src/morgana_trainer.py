# Based on Google Inc MINST model training example

import datetime
import os
import pickle
import random
import sys

import tensorflow as tf
from tensorflow.python.saved_model import (builder as saved_model_builder, signature_constants, signature_def_utils,
                                           tag_constants, utils)
from tensorflow.python.util import compat

from morgana_cnn_schema import MorganaCNNSchema
from morgana_config_handler import ENABLED_EMOTIONS, NUMBER_OF_EMOTIONS, TRAIN_DATA_FOLDER

FULL_TRAIN_SLICE = 5

MIN_STREAM_ACC = 0.6


def main(_):
    # Unpack args
    epochs = int(sys.argv[1])
    model_name = sys.argv[2]
    model_version = int(sys.argv[3])
    start_epoch = int(sys.argv[4])

    # Create session
    session = tf.InteractiveSession()

    # Create model
    cnn = MorganaCNNSchema()

    ###
    # Trainers
    ###

    # Output trainer (trains only output stream variables)
    train_vars = tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, "output")
    partial_trainer = tf.train.AdamOptimizer(1e-3).minimize(cnn.output_loss, var_list=train_vars)

    # Words trainer (trains only words stream variables)
    train_vars = tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, "words_stream")
    word_trainer = tf.train.AdamOptimizer(1e-3).minimize(cnn.word_loss, var_list=train_vars)

    # Chars trainer (trains only chars stream variables)
    train_vars = tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, "chars_stream")
    char_trainer = tf.train.AdamOptimizer(1e-3).minimize(cnn.char_loss, var_list=train_vars)

    # Raw Chars trainer (trains only rchar stream variables)
    train_vars = tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, "raw_char_stream")
    rchar_trainer = tf.train.AdamOptimizer(1e-3).minimize(cnn.rchar_loss, var_list=train_vars)

    tf.global_variables_initializer().run()

    ###
    # Checkpoints saver
    ###
    checkpoint_saver = tf.train.Saver()

    # Reload checkpoint if exists
    if start_epoch != 0:
        checkpoint_saver.restore(session, "tmp/" + model_name + "_{}.ckpt".format(start_epoch))

    # Redo last epoch because epoch could be not completed
    start_epoch -= 1 if start_epoch != 0 else 0

    # Stores a summary of the model, so epoch can be checked at tensorboard for debugging
    tf.summary.FileWriter('summary/{}'.format(model_name), session.graph)

    # Load batches
    train_batches, test_batches = load_batch_files()

    acc_global = 0
    acc_partial = 0

    # Training
    print('Training model {}<{}>'.format(model_name, model_version))

    iteration = 0
    do_test_step(test_batches, cnn, session, iteration)

    for epoch in range(start_epoch + 1, epochs):
        random.shuffle(train_batches)

        for iteration_slice in range(len(train_batches) // 100):
            iteration_slice_start = iteration_slice * 100
            iteration_slice_end = min((iteration_slice + 1) * 100, len(train_batches))

            # Train the first streams
            acc_word, loss_word = do_train_step(train_batches, cnn, epoch, model_name, checkpoint_saver, session,
                                                word_trainer, cnn.word_loss, cnn.word_accuracy,
                                                name="Words",
                                                start_iteration=iteration,
                                                iteration_slice_start=iteration_slice_start,
                                                iteration_slice_end=iteration_slice_end)
            acc_char, loss_char = do_train_step(train_batches, cnn, epoch, model_name, checkpoint_saver, session,
                                                char_trainer, cnn.char_loss, cnn.char_accuracy,
                                                name="Chars",
                                                start_iteration=iteration,
                                                iteration_slice_start=iteration_slice_start,
                                                iteration_slice_end=iteration_slice_end)
            acc_rchar, loss_rchar = do_train_step(train_batches, cnn, epoch, model_name, checkpoint_saver, session,
                                                  rchar_trainer, cnn.rchar_loss, cnn.rchar_accuracy,
                                                  name="Rchar",
                                                  start_iteration=iteration,
                                                  iteration_slice_start=iteration_slice_start,
                                                  iteration_slice_end=iteration_slice_end)

            # Trains the last stream if any of the first streams reached the minimun accuracy at train
            if acc_word > MIN_STREAM_ACC or acc_char > MIN_STREAM_ACC or acc_rchar > MIN_STREAM_ACC:

                acc_partial, loss_partial = do_train_step(train_batches, cnn, epoch, model_name, checkpoint_saver,
                                                          session,
                                                          partial_trainer, cnn.output_loss, cnn.output_accuracy,
                                                          name="Partial",
                                                          start_iteration=iteration,
                                                          iteration_slice_start=iteration_slice_start,
                                                          iteration_slice_end=iteration_slice_end)

            iteration += iteration_slice_end - iteration_slice_start
            do_test_step(test_batches, cnn, session, iteration)

            # Keeps track of the training accuracy of the model
            with open("{}_train_steps.csv".format(model_name), "a") as log:
                log.write("{},{},{},{},{},{}\n".format(iteration,
                                                       acc_global,
                                                       acc_partial,
                                                       acc_word,
                                                       acc_char,
                                                       acc_rchar))

    # Do a final test step
    do_test_step(test_batches, cnn, session, iteration)
    print('Done training!')

    # Save the model
    print("Storing the model")
    store_servable_model(model_name, session, cnn, model_version)
    print("Stored {}".format(model_name))


def store_servable_model(model_name, session, model, model_version):
    """Stores the trained model in a way that could be served
    by the tensorflow model server"""

    # Define export dir
    export_path_base = model_name
    export_path = os.path.join(
            compat.as_bytes(export_path_base),
            compat.as_bytes(str(model_version)))

    builder = saved_model_builder.SavedModelBuilder(export_path)

    # Creates the tensor info for the inputs and outputs
    classification_inputs_words = utils.build_tensor_info(model.words_features)
    classification_inputs_chars = utils.build_tensor_info(model.chars_features)
    classification_inputs_rchar = utils.build_tensor_info(model.raw_chars_features)
    classification_inputs_keep_prob = utils.build_tensor_info(model.dropout_keep_prob)
    classification_outputs_classes = utils.build_tensor_info(model.predictions)
    classification_outputs_scores = utils.build_tensor_info(model.scores)

    # Creates a signature
    prediction_signature = signature_def_utils.build_signature_def(
            inputs={"words": classification_inputs_words,
                    "chars": classification_inputs_chars,
                    "rchar": classification_inputs_rchar,
                    "loss": classification_inputs_keep_prob},
            outputs={'scores': classification_outputs_scores,
                     'predictions': classification_outputs_classes},
            method_name=signature_constants.PREDICT_METHOD_NAME)
    legacy_init_op = tf.group(tf.tables_initializer(), name='legacy_init_op')

    # Adds the signature to the servable model
    builder.add_meta_graph_and_variables(
            session, [tag_constants.SERVING],
            signature_def_map={
                'predict_tweets': prediction_signature
            },
            legacy_init_op=legacy_init_op)

    builder.save()


def load_batch_files():
    """Loads the list of aviable batchs for both training and testing.
    Returns firts the list of paths to train batches, and second the list to test batches"""
    batch_files = os.listdir(TRAIN_DATA_FOLDER)
    train_batches = [os.path.join(TRAIN_DATA_FOLDER, x) for x in batch_files if "train_batch" in x]
    test_batches = [os.path.join(TRAIN_DATA_FOLDER, x) for x in batch_files if "test_batch" in x]
    return train_batches, test_batches


def do_train_step(batches, cnn, epoch, output_folder, saver, sess, trainer, training_loss, training_accuracy, name="",
                  start_iteration=0, iteration_slice_start=0, iteration_slice_end=0):
    """Does a train step for the given trainer, using the passed batches.
    Returns the average accuracy and loss among all batches used"""
    total_loss = 0
    total_accuracy = 0
    total_batches = 0
    for batch_number in range(iteration_slice_start, iteration_slice_end):
        iteration = start_iteration + batch_number
        print("Iteration <{}>".format(name), iteration)

        # Loads the pickled batch
        with open(batches[batch_number], 'rb') as pickled:
            batch_data = pickle.load(pickled)

        # Training takes a while, so, some kind of info serves as some kind of heartbeat
        print("[{}] <{}> Iteration: {} - Epoch: {}".format(datetime.datetime.now(), name, iteration, epoch))

        # Runs the trainer and gets the asociated loss and accuracy values
        _, loss, accuracy = sess.run([trainer, training_loss, training_accuracy], feed_dict={
            cnn.words_features: batch_data[0],
            cnn.chars_features: batch_data[1],
            cnn.raw_chars_features: batch_data[2],
            cnn.input_y: batch_data[3],
            cnn.dropout_keep_prob: .5  # drop
        })

        total_batches += 1
        total_accuracy += float(accuracy)
        total_loss += float(loss)

    print('Step[{}]<{}>\n\tLoss: {}\n\tAccuracy:{}'.format(name, iteration,
                                                           total_loss / total_batches,
                                                           total_accuracy / total_batches)
          )
    save_path = saver.save(sess, "tmp/" + output_folder + "_{}.ckpt".format(epoch))
    print("Iteration training end: {}".format(save_path))

    return total_accuracy / total_batches, total_loss / total_batches


def do_test_step(batches, cnn, sess, iteration):
    """Does a test step for the full model, using the passed batches."""

    total_accuracy = 0
    total_batches = 0

    word = 0
    char = 0
    rchar = 0
    partial = 0

    random.shuffle(batches)

    confusion_matrix = [
        [0 for _ in range(NUMBER_OF_EMOTIONS)]
        for _ in range(NUMBER_OF_EMOTIONS)
    ]

    for batch_number in range(len(batches)):
        with open(batches[batch_number], 'rb') as pickled:
            batch_data = pickle.load(pickled)

        print("Test batch: {}/{}".format(batch_number, len(batches)))
        feed_dict = {
            cnn.words_features: batch_data[0],
            cnn.chars_features: batch_data[1],
            cnn.raw_chars_features: batch_data[2],
            cnn.input_y: batch_data[3],
            cnn.dropout_keep_prob: 1
        }

        accuracy, predictions, w_acc, c_acc, r_acc = sess.run(
                [cnn.output_accuracy, cnn.predictions, cnn.word_accuracy, cnn.char_accuracy, cnn.rchar_accuracy],
                feed_dict)

        total_batches += 1
        total_accuracy += accuracy
        word += w_acc
        char += c_acc
        rchar += r_acc

        for i in range(len(batch_data[3])):
            correct_class = int(batch_data[3][i])
            predicted = int(predictions[i])

            confusion_matrix[predicted][correct_class] += 1

    print('Test Step: \n\tTotal Acc:{}\n\tPart Acc:{}\n\tWord Acc:{}\n\tChar Acc:{}\n\tRcha Acc:{}'.format(
            total_accuracy / total_batches, partial / total_batches,
            word / total_batches, char / total_batches, rchar / total_batches))

    with open("test_steps.csv", "a") as log:
        log.write("{},{},{},{},{},{}\n".format(iteration,
                                               total_accuracy / total_batches,
                                               partial / total_batches,
                                               word / total_batches,
                                               char / total_batches,
                                               rchar / total_batches))

    calculate_all_f1_scores(confusion_matrix, "Morgana F1", iteration)


def calculate_all_f1_scores(confusion_matrix, tag, iteration):
    print("F1 Score {}".format(tag))

    f_scores = [0] * NUMBER_OF_EMOTIONS
    for label in range(NUMBER_OF_EMOTIONS):
        f_score = get_f_score_for_label(label, confusion_matrix)
        print("Label: {} - Fscore {}".format(ENABLED_EMOTIONS[label], f_score))
        f_scores[label] = f_score

    print("Mean Fscore {}".format(sum(f_scores) / NUMBER_OF_EMOTIONS))
    with open("{}F1.csv".format(tag), 'a') as output:
        line = ",".join([str(iteration)] + [str(f_score) for f_score in f_scores]) + "\n"
        output.write(line)


def get_f_score_for_label(label, matrix):
    true_positives = 0
    false_positives = 0
    false_negatives = 0
    for row_num, row in enumerate(matrix):

        if row_num != label:
            false_negatives += row[label]
            continue

        for column_num, column in enumerate(row):
            if column_num == label:
                true_positives += column
            else:
                false_positives += column

    if true_positives == 0:
        return 0

    precision = true_positives / (true_positives + false_positives)
    recall = true_positives / (true_positives + false_negatives)
    f_score = 2 * ((precision * recall) / (precision + recall))
    return f_score


if __name__ == '__main__':
    tf.app.run()
