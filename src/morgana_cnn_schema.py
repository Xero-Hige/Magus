import numpy as np
import tensorflow as tf

from cnn_schema import CNNSchema
from libs.db_tweet import DB_Handler
from libs.embedding_mapper import EmbeddingMapper
from libs.sentiments_handling import ANGER, ANTICIPATION, DISGUST, FEAR, JOY, NEUTRAL, SADNESS, SURPRISE, TRUST
from libs.tweet_parser import TweetParser
from tokenizer.char_tokenizer import CharTokenizer
from tokenizer.raw_char_tokenizer import RawCharTokenizer
from tokenizer.word_tokenizer import WordTokenizer

MAX_WORDS = 120
MAX_CHARS = 280

EMOTION_LOOKUP = {
    JOY:          0,
    TRUST:        1,
    FEAR:         2,
    SURPRISE:     3,
    SADNESS:      4,
    DISGUST:      5,
    ANGER:        6,
    ANTICIPATION: 7,
    NEUTRAL:      8
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
        convolution_layer_output_words, output_channels = self.create_conv_pool_layer(self.input_x_words,
                                                                                      embedding_size,
                                                                                      filter_sizes,
                                                                                      num_filters,
                                                                                      MAX_WORDS,
                                                                                      activation=tf.nn.tanh)

        words_dl, l2_loss = self.create_dense_layer(convolution_layer_output_words, output_channels, num_classes * 3,
                                                    name="words", l2_loss=l2_loss)

        convolution_layer_output_chars, output_channels = self.create_conv_pool_layer(self.input_x_chars,
                                                                                      embedding_size,
                                                                                      filter_sizes,
                                                                                      num_filters,
                                                                                      MAX_CHARS,
                                                                                      activation=tf.nn.tanh)

        chars_dl, l2_loss = self.create_dense_layer(convolution_layer_output_chars, output_channels, num_classes * 3,
                                                    name="chars", l2_loss=l2_loss)

        convolution_layer_output_r_chars, output_channels = self.create_conv_pool_layer(self.input_x_rchars,
                                                                                        embedding_size,
                                                                                        filter_sizes,
                                                                                        num_filters,
                                                                                        MAX_CHARS,
                                                                                        activation=tf.nn.tanh)

        r_chars_dl, l2_loss = self.create_dense_layer(convolution_layer_output_chars, output_channels, num_classes * 3,
                                                      name="raw_chars", l2_loss=l2_loss)

        dense_layers = tf.concat([words_dl, chars_dl, r_chars_dl], 1)

        # dropout_layer_output = self.create_dropout_layer(dense_layers, dropout_prob=self.dropout_keep_prob)
        scores, predictions, l2_loss = self.create_output_layer(dense_layers, num_classes * 9,
                                                                9,
                                                                l2_loss=l2_loss)

        print("Scores", scores)
        print("Predict", predictions)

        self.scores = scores
        self.predictions = predictions

        self.loss = self.get_loss(self.input_y, l2_loss, l2_reg_lambda, scores)
        self.accuracy = self.get_accuracy(self.input_y, predictions)

    @staticmethod
    def get_input_data(embedding_size=300):
        data = []
        with DB_Handler() as handler:
            tagged_tweets = handler.get_all_tagged()

            for tweet_data in tagged_tweets:
                try:
                    tweet = TweetParser.parse_from_json_file("../bulk/{}.json".format(tweet_data.id))
                except IOError:
                    try:
                        tweet = TweetParser.parse_from_json_file("../tweets/{}.json".format(tweet_data.id))
                    except IOError:
                        print("Missing tweet id: ", tweet_data.id)
                        continue

                data.append((tweet, tweet_data.get_tweet_emotion()))

        features = []
        labels = []

        for tweet, tag in data:
            if tag not in EMOTION_LOOKUP:
                continue

            features.append(str(tweet[TweetParser.TWEET_ID]))

            label = [0] * len(EMOTION_LOOKUP)
            label[EMOTION_LOOKUP[tag]] = 1
            labels.append(label)

        features = np.asarray(features, dtype=object)
        labels = np.asarray(labels, dtype=np.float32)

        return features, labels

    @staticmethod
    def map_batch(tweets):

        maps_words = []
        maps_chars = []
        maps_rchar = []

        for t_id in tweets:
            try:
                tweet = TweetParser.parse_from_json_file("../bulk/{}.json".format(t_id))
            except IOError:
                try:
                    tweet = TweetParser.parse_from_json_file("../tweets/{}.json".format(t_id))
                except IOError:
                    print("Missing tweet id: ", t_id)
                    continue

            tokens = WordTokenizer.tokenize_raw(tweet)
            maps_words.append(MorganaCNNSchema.W_MAPPER.map_features(tokens, t_id))

            tokens = CharTokenizer.tokenize_raw(tweet)
            maps_chars.append(MorganaCNNSchema.C_MAPPER.map_features(tokens, t_id))

            tokens = RawCharTokenizer.tokenize_raw(tweet)
            maps_rchar.append(MorganaCNNSchema.R_MAPPER.map_features(tokens, t_id))

        return np.asarray(maps_words), np.asarray(maps_chars), np.asarray(maps_rchar)
