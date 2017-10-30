import numpy as np
import tensorflow as tf
from cnn_network import CNNSchema
from gensim.models import KeyedVectors

from NNLayers import get_word_vector
from libs.db_tweet import DB_Handler
from libs.sentiments_handling import ANGER, ANGRY, ANTICIPATION, DISGUST, FEAR, HAPPY, JOY, NONE, SAD, SADNESS, \
    SURPRISE, TRUST
from libs.tweet_parser import TweetParser
from tokenizer.word_tokenizer import WordTokenizer

EMOTION_LOOKUP = {
    JOY: 1,
    TRUST: 2,
    FEAR: 3,
    SURPRISE: 4,
    SADNESS: 5,
    DISGUST: 6,
    ANGER: 7,
    ANTICIPATION: 8,
    NONE: 9
}

GROUP_LOOKUP = {
    HAPPY: EMOTION_LOOKUP[NONE] + 1,
    SAD: EMOTION_LOOKUP[NONE] + 2,
    ANGRY: EMOTION_LOOKUP[NONE] + 2,
    NONE: EMOTION_LOOKUP[NONE] + 4,
}


class AttardiCNNSchema(CNNSchema):
    """
    A CNN for text classification.
    Uses an embedding layer, followed by a convolutional, max-pooling and softmax layer.
    """

    def __init__(self, sequence_length, num_classes, vocab_size, embedding_size, filter_sizes, num_filters,
                 l2_reg_lambda=0.0):

        # Placeholders for input, output and dropout
        super().__init__(sequence_length, num_classes, vocab_size, embedding_size, filter_sizes, num_filters,
                         l2_reg_lambda)
        input_features, input_labels = self.create_input_layer(num_classes, embedding_size)
        self.dropout_keep_prob = tf.placeholder(tf.float32, name="dropout_keep_prob")
        l2_loss = tf.constant(0.0)

        self.input_x = input_features
        self.input_y = input_labels

        # TODO: Check
        convolution_layer_output, output_channels = self.create_conv_pool_layer(self.input_x,
                                                                                embedding_size,
                                                                                filter_sizes,
                                                                                num_filters,
                                                                                vocab_size)

        dropout_layer_output = self.create_dropout_layer(convolution_layer_output,
                                                         dropout_prob=self.dropout_keep_prob)

        scores, predictions, l2_loss = self.create_output_layer(dropout_layer_output, output_channels, num_classes,
                                                                l2_loss=l2_loss)

        self.loss = self.get_loss(self.input_y, l2_loss, l2_reg_lambda, scores)
        self.accuracy = self.get_accuracy(self.input_y, predictions)

    @staticmethod
    def get_input_data():
        word_vectors = KeyedVectors.load('./mymodel.mdl')

        data = []
        with DB_Handler() as handler:
            tagged_tweets = handler.get_all_tagged()

            for tweet_data in tagged_tweets:
                if tweet_data.get_tweet_sentiment() == "-":
                    continue

                try:
                    tweet = TweetParser.parse_from_json_file("../bulk/{}.json".format(tweet_data.id))
                except IOError:
                    try:
                        tweet = TweetParser.parse_from_json_file("../tweets/{}.json".format(tweet_data.id))
                    except IOError:
                        print("Missing tweet id: ", tweet_data.id)
                        continue

                data.append((tweet, tweet_data.get_emotions_list(), tweet_data.get_tweet_group()))

        features = []
        labels = []

        for tweet, emotions, tag in data:
            tweet_vectors = []
            tokens = WordTokenizer.tokenize_raw(tweet)

            for word in tokens:
                tweet_vectors.append(get_word_vector(word, word_vectors))

            while len(tweet_vectors) < 70:
                tweet_vectors.append(np.asarray([[0]] * 300))

            features.append(tweet_vectors)

            label = [0] * 14
            label[GROUP_LOOKUP[tag]] = 1

            # for emotion_value, emotion_tag in emotions:
            #    label[EMOTION_LOOKUP[emotion_tag]] = emotion_value / 10

            labels.append(label[10:12])

        features = np.asarray(features, dtype=np.float32)
        labels = np.asarray(labels, dtype=np.float32)

        return features, labels
