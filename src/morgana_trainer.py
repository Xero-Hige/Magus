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
from morgana_config_handler import NUMBER_OF_EMOTIONS

TEST_STEP = 5

MIN_STREAM_ACC = 0.6


def main(_):
    # Unpack args
    iterations = int(sys.argv[1])
    model_name = sys.argv[2]
    model_version = int(sys.argv[3])
    start_it = int(sys.argv[4])

    # Create session
    session = tf.InteractiveSession()

    # Create model
    cnn = MorganaCNNSchema()

    ###
    # Trainers
    ###
    # Global trainer (trains only global stream variables)
    train_vars = tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, "global")
    global_trainer = tf.train.AdamOptimizer(1e-3).minimize(cnn.loss, var_list=train_vars)

    # Partial trainer (trains only partial stream variables)
    train_vars = tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, "partial")
    partial_trainer = tf.train.AdamOptimizer(1e-3).minimize(cnn.partial_loss, var_list=train_vars)

    # Words trainer (trains only words stream variables)
    train_vars = tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, "words_stream")
    word_trainer = tf.train.AdamOptimizer(1e-3).minimize(cnn.word_loss, var_list=train_vars)

    # Chars trainer (trains only chars stream variables)
    train_vars = tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, "chars_stream")
    char_trainer = tf.train.AdamOptimizer(1e-3).minimize(cnn.char_loss, var_list=train_vars)

    # Raw Chars trainer (trains only rchar stream variables)
    train_vars = tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, "rchar_stream")
    rchar_trainer = tf.train.AdamOptimizer(1e-3).minimize(cnn.rchar_loss, var_list=train_vars)

    # Full trainers (trains variables from every connected stream)
    global_full_trainer = tf.train.AdamOptimizer(1e-3).minimize(cnn.loss)
    partial_full_trainer = tf.train.AdamOptimizer(1e-3).minimize(cnn.partial_loss)
    ###

    tf.global_variables_initializer().run()

    ###
    # Checkpoints saver
    ###
    checkpoint_saver = tf.train.Saver()

    # Reload checkpoint if exists
    if start_it != 0:
        checkpoint_saver.restore(session, "tmp/" + model_name + "_{}.ckpt".format(start_it))

    # Redo last iteration because it could be not completed
    start_it -= 1 if start_it != 0 else 0

    # Stores a summary of the model, so it can be checked at tensorboard for debugging
    tf.summary.FileWriter('summary/{}'.format(model_name), session.graph)

    # Load batches
    train_batches, test_batches = load_batch_files()

    acc_char = 0
    acc_word = 0
    acc_rchar = 0
    acc_global = 0
    acc_partial = 0

    # Training
    print('Training model {}<{}>'.format(model_name, model_version))

    for it in range(start_it + 1, iterations):
        # Train the first streams
        acc_word, loss_word = do_train_step(train_batches, cnn, it, model_name, checkpoint_saver, session,
                                            word_trainer, cnn.word_loss, cnn.word_accuracy,
                                            name="Words", prev_acc=acc_word)
        acc_char, loss_char = do_train_step(train_batches, cnn, it, model_name, checkpoint_saver, session,
                                            char_trainer, cnn.char_loss, cnn.char_accuracy,
                                            name="Chars", prev_acc=acc_char)
        acc_rchar, loss_rchar = do_train_step(train_batches, cnn, it, model_name, checkpoint_saver, session,
                                              rchar_trainer, cnn.rchar_loss, cnn.rchar_accuracy,
                                              name="Rchar", prev_acc=acc_rchar)

        # Trains the lasts streams if any of the first streams reached the minimun accuracy at train
        if acc_word > MIN_STREAM_ACC or acc_char > MIN_STREAM_ACC or acc_rchar > MIN_STREAM_ACC:
            # Trains the full net, only 1 of TEST_STEP times, and only after the test step
            trainer = global_full_trainer if it % TEST_STEP == 1 else global_trainer
            acc_global, loss_global = do_train_step(train_batches, cnn, it, model_name, checkpoint_saver, session,
                                                    trainer, cnn.loss, cnn.accuracy,
                                                    name="Global", prev_acc=acc_global)

            trainer = partial_full_trainer if it % TEST_STEP == 1 else partial_trainer
            acc_partial, loss_partial = do_train_step(train_batches, cnn, it, model_name, checkpoint_saver, session,
                                                      trainer, cnn.partial_loss, cnn.partial_accuracy,
                                                      name="Partial", prev_acc=acc_partial)
        if (it % TEST_STEP) == 0:
            do_test_step(test_batches, cnn, session)

        # Keeps track of the training accuracy of the model
        with open("{}_train_steps.csv".format(model_name), "a") as log:
            log.write("{},{},{},{},{},{}\n".format(it,
                                                   acc_global,
                                                   acc_partial,
                                                   acc_word,
                                                   acc_char,
                                                   acc_rchar))

    # Do a final test step
    do_test_step(test_batches, cnn, session)
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
            outputs={'scores': classification_outputs_scores, 'predictions': classification_outputs_classes},
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
    batch_files = os.listdir("/media/hige/320/train_data/")
    train_batches = ["/media/hige/320/train_data/" + x for x in batch_files if "train_batch" in x]
    test_batches = ["/media/hige/320/train_data/" + x for x in batch_files if "test_batch" in x]
    return train_batches, test_batches


def do_train_step(batches, cnn, it, output_folder, saver, sess, trainer, training_loss, training_accuracy, name="",
                  prev_acc=1):
    """Does a train step for the given trainer, using the passed batches.
    Returns the average accuracy and loss among all batches used"""
    print("Iteration <{}>".format(name), it)
    random.shuffle(batches)
    total_loss = 0
    total_accuracy = 0
    total_batches = 0
    for batch_number in range(len(batches)):
        # Loads the pickled batch
        with open(batches[batch_number], 'rb') as pickled:
            batch_data = pickle.load(pickled)

        # Training takes a while, so, some kind of info serves as some kind of heartbeat
        print("[{}] Iteration{}: {} - Batch: {}/{}".format(datetime.datetime.now(), name, it, batch_number + 1,
                                                           len(batches)))

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

    print('Step[{}]<{}>\n\tLoss: {}\n\tAccuracy:{}'.format(name, it,
                                                           total_loss / total_batches,
                                                           total_accuracy / total_batches)
          )
    save_path = saver.save(sess, "tmp/" + output_folder + "_{}.ckpt".format(it))
    print("Iteration training end: {}".format(save_path))

    return total_accuracy / total_batches, total_loss / total_batches


def do_test_step(batches, cnn, sess):
    """Does a test step for the full model, using the passed batches."""

    total_accuracy = 0
    total_batches = 0

    word = 0
    char = 0
    rchar = 0
    partial = 0

    random.shuffle(batches)

    confusion_matrix_global = [
        [0 for _ in range(NUMBER_OF_EMOTIONS)]
        for _ in range(NUMBER_OF_EMOTIONS)
    ]
    confusion_matrix_partial = [
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

        accuracy, predictions, \
        w_acc, c_acc, r_acc, \
        partial_acc, partial_pred = sess.run(
                [cnn.accuracy, cnn.predictions,
                 cnn.word_accuracy, cnn.char_accuracy, cnn.rchar_accuracy,
                 cnn.partial_accuracy, cnn.partial_predictions],
                feed_dict)

        total_batches += 1
        total_accuracy += accuracy
        word += w_acc
        char += c_acc
        rchar += r_acc
        partial += partial_acc

        for i in range(len(batch_data[3])):
            correct_class = int(batch_data[3][i])
            partial_predicted = int(partial_pred[i])
            global_predicted = int(predictions[i])

            confusion_matrix_global[global_predicted][correct_class] += 1
            confusion_matrix_partial[partial_predicted][correct_class] += 1

    print('Test Step: \n\tTotal Acc:{}\n\tPart Acc:{}\n\tWord Acc:{}\n\tChar Acc:{}\n\tRcha Acc:{}'.format(
            total_accuracy / total_batches, partial / total_batches,
            word / total_batches, char / total_batches, rchar / total_batches))

    print("Fscore Global")
    total_fscore = 0
    for label in range(NUMBER_OF_EMOTIONS):
        f_score = get_f_score_for_label(label, confusion_matrix_global)
        print("Label: {} - Fscore {}".format(label, f_score))
        total_fscore += f_score
    print("Mean Fscore {}".format(total_fscore / NUMBER_OF_EMOTIONS))

    print("Fscore Partial")
    total_fscore = 0
    for label in range(NUMBER_OF_EMOTIONS):
        f_score = get_f_score_for_label(label, confusion_matrix_partial)
        print("Label: {} - Fscore {}".format(label, f_score))
        total_fscore += f_score
    print("Mean Fscore {}".format(total_fscore / NUMBER_OF_EMOTIONS))

    with open("test_steps.csv", "a") as log:
        log.write("{},{},{},{},{}\n".format(total_accuracy / total_batches,
                                            partial / total_batches,
                                            word / total_batches,
                                            char / total_batches,
                                            rchar / total_batches))


def get_f_score_for_label(label, matrix):
    true_positives = 0
    false_positives = 0
    false_negatives = 0
    for row_num, row in enumerate(matrix):
        if row_num == label:
            for column_num, column in enumerate(row):
                if column_num == label:
                    true_positives += column
                else:
                    false_positives += column
            continue
        false_negatives += row[label]
    precision = true_positives / (true_positives + false_positives)
    recall = true_positives / (true_positives + false_negatives)
    f_score = 2 * ((precision * recall) / (precision + recall))
    return f_score


if __name__ == '__main__':
    tf.app.run()
