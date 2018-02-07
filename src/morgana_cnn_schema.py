import numpy as np
import tensorflow as tf

from cnn_schema import CNNSchema
from libs.db_tweet import DB_Handler
from libs.embedding_mapper import EmbeddingMapper
from libs.sentiments_handling import ANGER, FEAR, JOY, NEUTRAL, SADNESS
from libs.tweet_parser import TweetParser
from tokenizer.char_tokenizer import CharTokenizer
from tokenizer.raw_char_tokenizer import RawCharTokenizer
from tokenizer.word_tokenizer import WordTokenizer

MAX_WORDS = 120
MAX_CHARS = 320

EMOTION_LOOKUP = {
    JOY:     0,
    # TRUST:        1,
    FEAR:    1,
    # SURPRISE:     3,
    SADNESS: 2,
    # DISGUST:      5,
    ANGER:   3,
    # ANTICIPATION: 7,
    NEUTRAL: 4
}


class MorganaCNNSchema(CNNSchema):
    """
    A CNN for text classification.
    Uses an embedding layer, followed by a convolutional, max-pooling and softmax layer.
    """

    W_MAPPER = EmbeddingMapper("./wordsEmbeddings.mdl", MAX_WORDS, 300)
    C_MAPPER = EmbeddingMapper("./charsEmbeddings.mdl", MAX_CHARS, 300)
    R_MAPPER = EmbeddingMapper("./rCharsEmbeddings.mdl", MAX_CHARS, 300)

    def __init__(self, num_classes, vocab_size, embedding_size, filter_sizes, num_filters,
                 l2_reg_lambda=0.0):

        # Placeholders for input, output and dropout
        super().__init__(num_classes, vocab_size, embedding_size, filter_sizes, num_filters,
                         l2_reg_lambda)

        words_input_features, input_labels = self.create_input_layer(num_classes, embedding_size, name="_words")
        chars_input_features, input_labels = self.create_input_layer(num_classes, embedding_size, name="_chars")
        r_chars_input_features, input_labels = self.create_input_layer(num_classes, embedding_size, name="_rchars")

        self.dropout_keep_prob = tf.placeholder(tf.float32, name="dropout_keep_prob")
        l2_loss = tf.constant(0.0)

        self.input_x_words = words_input_features
        self.input_x_chars = chars_input_features
        self.input_x_rchars = r_chars_input_features

        self.input_y = input_labels

        # TODO: Check
        output_layers_size = num_classes

        with tf.name_scope("words_stream"):
            hidden_words, words_dl = self.create_first_combs(self.input_x_words, embedding_size, filter_sizes, l2_loss,
                                                             num_filters, MAX_WORDS, "words",
                                                             output_size=output_layers_size,
                                                             hidden_layer_size=int(output_layers_size * 102.4),
                                                             prefix="words_stream")

            word_predictions = tf.argmax(words_dl, 1)
        self.word_loss = self.get_loss(self.input_y, l2_loss, l2_reg_lambda, words_dl)
        self.word_accuracy = self.get_accuracy(self.input_y, word_predictions)

        with tf.name_scope("chars_stream"):
            hidden_chars, chars_dl = self.create_first_combs(self.input_x_chars, embedding_size, filter_sizes, l2_loss,
                                                             num_filters, MAX_CHARS, "chars",
                                                             output_size=output_layers_size,
                                                             hidden_layer_size=int(output_layers_size * 102.4),
                                                             prefix="chars_stream")

            char_predictions = tf.argmax(chars_dl, 1)
        self.char_loss = self.get_loss(self.input_y, l2_loss, l2_reg_lambda, chars_dl)
        self.char_accuracy = self.get_accuracy(self.input_y, char_predictions)

        with tf.name_scope("rchar_stream"):
            hidden_rchar, r_chars_dl = self.create_first_combs(self.input_x_rchars, embedding_size, filter_sizes,
                                                               l2_loss,
                                                               num_filters, MAX_CHARS, "rchars",
                                                               output_size=output_layers_size,
                                                               hidden_layer_size=int(output_layers_size * 102.4),
                                                               prefix="rchar_stream")

            rchar_predictions = tf.argmax(r_chars_dl, 1)
        self.rchar_loss = self.get_loss(self.input_y, l2_loss, l2_reg_lambda, r_chars_dl)
        self.rchar_accuracy = self.get_accuracy(self.input_y, rchar_predictions)

        with tf.name_scope("global"):
            dense_layers = tf.concat([hidden_words, hidden_chars, hidden_rchar], 1)
            dropout_concat = self.create_dropout_layer(dense_layers, dropout_prob=self.dropout_keep_prob)

            dense_layer = MorganaCNNSchema.create_dense_layer(dropout_concat, int(output_layers_size * 102.4) * 3,
                                                              int(output_layers_size * 102.4), "Extract",
                                                              prefix="global")
            dropout_redux = self.create_dropout_layer(dense_layer, dropout_prob=self.dropout_keep_prob)

            scores, predictions = self.create_output_layer(dropout_redux,
                                                           int(output_layers_size * 102.4),
                                                           num_classes,
                                                           l2_loss=l2_loss)

        self.scores = scores
        self.predictions = predictions

        self.loss = self.get_loss(self.input_y, l2_loss, l2_reg_lambda, scores)
        self.accuracy = self.get_accuracy(self.input_y, predictions)

    def create_first_combs(self,
                           input_layer,
                           embedding_size,
                           filter_sizes,
                           l2_loss,
                           num_filters,
                           number_of_features,
                           name,
                           output_size,
                           hidden_layer_size=1024,
                           prefix=""):

        convolution_layer_output, output_channels = self.create_conv_pool_layer(input_layer,
                                                                                embedding_size,
                                                                                filter_sizes,
                                                                                num_filters,
                                                                                number_of_features,
                                                                                activation=tf.nn.tanh)

        dense_layer = self.create_dense_layer(convolution_layer_output, output_channels, hidden_layer_size,
                                              name=name, l2_loss=l2_loss, prefix=prefix)

        dropout = self.create_dropout_layer(dense_layer, dropout_prob=self.dropout_keep_prob)

        redux_dense_layer = self.create_dense_layer(dropout, hidden_layer_size, output_size,
                                                    name="redux_{}".format(name), l2_loss=l2_loss, prefix=prefix)
        return dense_layer, redux_dense_layer

    @staticmethod
    def get_input_data(embedding_size=300):
        data = []
        with DB_Handler() as handler:
            tagged_tweets = handler.get_all_tagged()

            for tweet_data in tagged_tweets:
                # TODO: Remove

                """try:
                    tweet = TweetParser.parse_from_json_file("../bulk/{}.json".format(tweet_data.id))
                    with open("../bulk/{}.json".format(tweet_data.id)) as f_in:
                        t_string = f_in.read()
                except IOError:
                    try:
                        tweet = TweetParser.parse_from_json_file("../tweets/{}.json".format(tweet_data.id))
                        with open("../tweets/{}.json".format(tweet_data.id)) as f_in:
                            t_string = f_in.read()

                    except IOError:
                        print("Missing tweet id: ", tweet_data.id)
                        continue

                if tweet_data.get_tweet_emotion() == NEUTRAL and tweet["tweet_lang"].lower() == "en":
                    with open("../neutrals/{}.json".format(tweet_data.id), 'w') as output:
                        output.write(t_string)

                if "fx" not in tweet_data.id:
                    continue"""

                try:
                    tweet = TweetParser.parse_from_json_file("../database/{}.json".format(tweet_data.id))
                except IOError:
                    continue

                data.append((tweet, tweet_data.get_tweet_emotion()))

        features = []
        labels = []

        for tweet, tag in data:
            if tag not in EMOTION_LOOKUP:
                tag = NEUTRAL

            features.append(str(tweet[TweetParser.TWEET_ID]))

            #            label = [0] * len(EMOTION_LOOKUP)
            #            label[EMOTION_LOOKUP[tag]] = 1
            labels.append(EMOTION_LOOKUP[tag])

        features = np.asarray(features, dtype=object)
        labels = np.asarray(labels, dtype=np.float32)

        return features, labels

    @staticmethod
    def map_batch(tweets):

        maps_words = []
        maps_chars = []
        maps_rchar = []

        for t_id in tweets:
            """try:
                tweet = TweetParser.parse_from_json_file("../bulk/{}.json".format(t_id))
            except IOError:
                try:
                    tweet = TweetParser.parse_from_json_file("../tweets/{}.json".format(t_id))
                except IOError:
                    print("Missing tweet id: ", t_id)
                    continue"""
            try:
                tweet = TweetParser.parse_from_json_file("../database/{}.json".format(t_id))
            except IOError:
                print("ERROR!!!!!!!!!!!!!!!!!!", t_id)
                continue

            tokens = WordTokenizer.tokenize_raw(tweet)
            maps_words.append(MorganaCNNSchema.W_MAPPER.map_features(tokens, t_id))

            tokens = CharTokenizer.tokenize_raw(tweet)
            maps_chars.append(MorganaCNNSchema.C_MAPPER.map_features(tokens, t_id))

            tokens = RawCharTokenizer.tokenize_raw(tweet)
            maps_rchar.append(MorganaCNNSchema.R_MAPPER.map_features(tokens, t_id))

        return np.asarray(maps_words), np.asarray(maps_chars), np.asarray(maps_rchar)
