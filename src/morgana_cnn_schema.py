import os

import numpy as np
import tensorflow as tf

from cnn_schema import CNNSchema
from libs.db_tweet import DB_Handler
from libs.embedding_mapper import EmbeddingMapper
from libs.tweet_parser import TweetParser
from morgana_config_handler import EMBEDDINGS_FILES, EMBEDDING_SIZES, ENABLED_EMOTIONS, FILTER_SIZES, \
    HIDDEN_LAYERS_SIZE, MAX_FEATURES, NUMBER_OF_EMOTIONS, NUMBER_OF_FILTERS, TWEETS_DIRS
from tokenizer.char_tokenizer import CharTokenizer
from tokenizer.raw_char_tokenizer import RawCharTokenizer
from tokenizer.word_tokenizer import WordTokenizer


class MorganaCNNSchema(CNNSchema):
    """
    TODO
    A CNN for text classification.
    Uses an embedding layer, followed by a convolutional, max-pooling and softmax layer.
    """

    # Embedding size for each feature
    WORDS_EMBEDDING_SIZE = EMBEDDING_SIZES["words"]
    CHARS_EMBEDDING_SIZE = EMBEDDING_SIZES["chars"]
    RAW_CHARS_EMBEDDING_SIZE = EMBEDDING_SIZES["raw_chars"]

    # Max numbers of features per tweet
    MAX_WORDS = MAX_FEATURES["words"]
    MAX_CHARS = MAX_FEATURES["chars"]
    MAX_RAW_CHARS = MAX_FEATURES["raw_chars"]

    # Embeddings mappers
    W_MAPPER = EmbeddingMapper("./{}.mdl".format(EMBEDDINGS_FILES["words"]), MAX_WORDS, WORDS_EMBEDDING_SIZE)
    C_MAPPER = EmbeddingMapper("./{}.mdl".format(EMBEDDINGS_FILES["chars"]), MAX_CHARS, CHARS_EMBEDDING_SIZE)
    R_MAPPER = EmbeddingMapper("./{}.mdl".format(EMBEDDINGS_FILES["raw_chars"]), MAX_RAW_CHARS,
                               RAW_CHARS_EMBEDDING_SIZE)

    def __init__(self, l2_reg_lambda=0.0):

        number_of_clases = NUMBER_OF_EMOTIONS
        ####
        # Inputs
        ####

        # Placeholders for input values
        super().__init__(l2_reg_lambda)
        words_input_features, input_labels = self.create_input_layer(number_of_clases,
                                                                     MorganaCNNSchema.WORDS_EMBEDDING_SIZE,
                                                                     name="_words")
        chars_input_features, input_labels = self.create_input_layer(number_of_clases,
                                                                     MorganaCNNSchema.CHARS_EMBEDDING_SIZE,
                                                                     name="_chars")
        r_chars_input_features, input_labels = self.create_input_layer(number_of_clases,
                                                                       MorganaCNNSchema.RAW_CHARS_EMBEDDING_SIZE,
                                                                       name="_rchars")

        self.dropout_keep_prob = tf.placeholder(tf.float32, name="dropout_keep_prob")
        l2_loss = tf.constant(0.0)

        # Bind placeholders to class atributes
        self.words_features = words_input_features
        self.chars_features = chars_input_features
        self.raw_chars_features = r_chars_input_features

        self.input_y = input_labels

        ####
        # Intermediate streams
        ####
        ##Words
        with tf.name_scope("words_stream"):
            hidden_words, words_dl = self.__create_stream(self.words_features,
                                                          MorganaCNNSchema.WORDS_EMBEDDING_SIZE,
                                                          FILTER_SIZES["words"],
                                                          l2_loss,
                                                          NUMBER_OF_FILTERS["words"],
                                                          MorganaCNNSchema.MAX_WORDS,
                                                          "words",
                                                          output_size=number_of_clases,
                                                          hidden_layer_size=HIDDEN_LAYERS_SIZE["words"],
                                                          prefix="words_stream")

            word_predictions = tf.argmax(words_dl, 1)
        self.word_loss = self.get_loss(self.input_y, l2_loss, l2_reg_lambda, words_dl)
        self.word_accuracy = self.get_accuracy(self.input_y, word_predictions)

        ##Chars
        with tf.name_scope("chars_stream"):
            hidden_chars, chars_dl = self.__create_stream(self.chars_features,
                                                          MorganaCNNSchema.CHARS_EMBEDDING_SIZE,
                                                          FILTER_SIZES["chars"],
                                                          l2_loss,
                                                          NUMBER_OF_FILTERS["chars"],
                                                          MorganaCNNSchema.MAX_CHARS,
                                                          "chars",
                                                          output_size=number_of_clases,
                                                          hidden_layer_size=HIDDEN_LAYERS_SIZE["chars"],
                                                          prefix="chars_stream")

            char_predictions = tf.argmax(chars_dl, 1)
        self.char_loss = self.get_loss(self.input_y, l2_loss, l2_reg_lambda, chars_dl)
        self.char_accuracy = self.get_accuracy(self.input_y, char_predictions)

        ##Raw chars
        with tf.name_scope("rchar_stream"):
            hidden_rchar, r_chars_dl = self.__create_stream(self.raw_chars_features,
                                                            MorganaCNNSchema.RAW_CHARS_EMBEDDING_SIZE,
                                                            FILTER_SIZES["raw_chars"],
                                                            l2_loss,
                                                            NUMBER_OF_FILTERS["raw_chars"],
                                                            MorganaCNNSchema.MAX_RAW_CHARS,
                                                            "rchars",
                                                            output_size=number_of_clases,
                                                            hidden_layer_size=HIDDEN_LAYERS_SIZE["raw_chars"],
                                                            prefix="rchar_stream")

            rchar_predictions = tf.argmax(r_chars_dl, 1)
        self.rchar_loss = self.get_loss(self.input_y, l2_loss, l2_reg_lambda, r_chars_dl)
        self.rchar_accuracy = self.get_accuracy(self.input_y, rchar_predictions)

        ###
        # Complex layers
        ###
        ##Scores stream
        with tf.name_scope("partial"):
            dense_layers = tf.concat([words_dl, chars_dl, r_chars_dl], 1)
            dense_layer = MorganaCNNSchema.create_dense_layer(dense_layers,
                                                              number_of_clases * 3,
                                                              HIDDEN_LAYERS_SIZE["scores_stream"],
                                                              "Extract",
                                                              prefix="partial")

            dropout_redux = self.create_dropout_layer(dense_layer, dropout_prob=self.dropout_keep_prob)
            scores, predictions = self.create_output_layer(dropout_redux,
                                                           HIDDEN_LAYERS_SIZE["scores_stream"],
                                                           number_of_clases,
                                                           l2_loss=l2_loss,
                                                           prefix="partial")

        self.partial_scores = scores
        self.partial_predictions = predictions

        self.partial_loss = self.get_loss(self.input_y, l2_loss, l2_reg_lambda, scores)
        self.partial_accuracy = self.get_accuracy(self.input_y, predictions)

        ##Global Stream
        with tf.name_scope("global"):
            dense_layers = tf.concat([hidden_words, hidden_chars, hidden_rchar], 1)
            dropout_concat = self.create_dropout_layer(dense_layers, dropout_prob=self.dropout_keep_prob)

            dense_layer = MorganaCNNSchema.create_dense_layer(dropout_concat,
                                                              HIDDEN_LAYERS_SIZE["words"] +
                                                              HIDDEN_LAYERS_SIZE["chars"] +
                                                              HIDDEN_LAYERS_SIZE["raw_chars"],
                                                              HIDDEN_LAYERS_SIZE["global_stream"],
                                                              "Extract",
                                                              prefix="global")

            dropout_redux = self.create_dropout_layer(dense_layer, dropout_prob=self.dropout_keep_prob)
            scores, predictions = self.create_output_layer(dropout_redux,
                                                           HIDDEN_LAYERS_SIZE["global_stream"],
                                                           number_of_clases,
                                                           l2_loss=l2_loss,
                                                           prefix="global")

        self.scores = scores
        self.predictions = predictions

        self.loss = self.get_loss(self.input_y, l2_loss, l2_reg_lambda, scores)
        self.accuracy = self.get_accuracy(self.input_y, predictions)

    def __create_stream(self,
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
        """Creates a stream, composed by a:
            -ConvPoll layer
            -Dense layer (size of hidden)
            -Dense layer (size of output)
            
            Returns the created hidden and output layer"""
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
    def get_input_data():
        """Loads and returns the tagged dataset.
        Returns two np.arrays, the first containing the tweets ids and the second the labels.
        Both returning arrays have the same length and order. Labels are marked as the index of the class in the
        enabled emotion list at the config file.
         
        Note: Non enabled emotion tweets are omitted"""

        data = []

        # Load tweets stored in disk
        with DB_Handler() as handler:
            tagged_tweets = handler.get_all_tagged()

            for tweet_data in tagged_tweets:
                tweet = None
                try:
                    for tweet_dir in TWEETS_DIRS:
                        path = "../{}/{}.json".format(tweet_dir, tweet_data.id)
                        if os.path.exists(path):
                            tweet = TweetParser.parse_from_json_file(path)
                            break

                except IOError:
                    continue

                if not tweet:
                    continue

                data.append((tweet, tweet_data.get_tweet_emotion()))

        # Creates ids / labels array
        tweets_ids = []
        tweets_labels = []

        for tweet, tag in data:
            if tag not in ENABLED_EMOTIONS:
                print("Not tag {}".format(tag))
                continue

            tweets_ids.append(str(tweet[TweetParser.TWEET_ID]))
            tweets_labels.append(ENABLED_EMOTIONS.index(tag))

        tweets_ids = np.asarray(tweets_ids, dtype=object)
        tweets_labels = np.asarray(tweets_labels, dtype=np.float32)

        return tweets_ids, tweets_labels

    @staticmethod
    def map_batch(tweets):
        """Given a list of tweet ids as string, returns a tuple of np.arrays with the 
        features map for each given tweet id."""

        maps_words = []
        maps_chars = []
        maps_rchar = []

        for t_id in tweets:
            for tweet_dir in TWEETS_DIRS:
                path = "../{}/{}.json".format(tweet_dir, t_id)
                if os.path.exists(path):
                    tweet = TweetParser.parse_from_json_file(path)

            tokens = WordTokenizer.tokenize_raw(tweet)
            maps_words.append(MorganaCNNSchema.W_MAPPER.map_features(tokens, t_id))

            tokens = CharTokenizer.tokenize_raw(tweet)
            maps_chars.append(MorganaCNNSchema.C_MAPPER.map_features(tokens, t_id))

            tokens = RawCharTokenizer.tokenize_raw(tweet)
            maps_rchar.append(MorganaCNNSchema.R_MAPPER.map_features(tokens, t_id))

        return np.asarray(maps_words), np.asarray(maps_chars), np.asarray(maps_rchar)
