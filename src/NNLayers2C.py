import random
import re

import numpy as np
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
    ANGRY: EMOTION_LOOKUP[NONE] + 3,
    NONE: EMOTION_LOOKUP[NONE] + 4,
}


def clean_str(string):
    """
    Tokenization/string cleaning for all datasets except for SST.
    Original taken from https://github.com/yoonkim/CNN_sentence/blob/master/process_data.py
    """
    string = re.sub(r"[^A-Za-z0-9(),!?\'\`]", " ", string)
    string = re.sub(r"\'s", " \'s", string)
    string = re.sub(r"\'ve", " \'ve", string)
    string = re.sub(r"n\'t", " n\'t", string)
    string = re.sub(r"\'re", " \'re", string)
    string = re.sub(r"\'d", " \'d", string)
    string = re.sub(r"\'ll", " \'ll", string)
    string = re.sub(r",", " , ", string)
    string = re.sub(r"!", " ! ", string)
    string = re.sub(r"\(", " \( ", string)
    string = re.sub(r"\)", " \) ", string)
    string = re.sub(r"\?", " \? ", string)
    string = re.sub(r"\s{2,}", " ", string)
    return string.strip().lower()


def get_input_data():
    word_vectors = KeyedVectors.load('./mymodel.mdl')
    missing = []
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

            # print("[", tweet_data.get_tweet_sentiment(), "] ", tweet[TweetParser.TWEET_TEXT])
            # print("( https://magus-catalog.herokuapp.com/classify/{} )".format(tweet_data.id))

    features = []
    labels = []

    for tweet, emotions, tag in data:
        tweet_vectors = []
        tokens = WordTokenizer.tokenize_raw(tweet)

        for word in tokens:
            tweet_vectors.append(get_word_vector(word, word_vectors))

        while len(tweet_vectors) < 70:
            tweet_vectors.append(np.asarray([[0]] * 300))

        # tweet_vector = np.append([], tweet_vectors)

        features.append(tweet_vectors)

        label = [0] * 14
        label[GROUP_LOOKUP[tag]] = 1

        # for emotion_value, emotion_tag in emotions:
        #    label[EMOTION_LOOKUP[emotion_tag]] = emotion_value / 10

        labels.append(label[10:])

    # print(len(tweet_vectors))

    features = np.asarray(features, dtype=np.float32)
    labels = np.asarray(labels, dtype=np.float32)

    # print(features[0])
    # input()
    # print(train_labels)

    return features, labels


def load_data_and_labels(positive_data_file, negative_data_file):
    """
    Loads MR polarity data from files, splits the data into words and generates labels.
    Returns split sentences and labels.
    """
    # Load data from files
    # positive_examples = list(open(positive_data_file, "r").readlines())
    positive_examples = [
        [
            [
                [random.random()], [1]
            ] * 150
        ] * 70 for _ in range(200)
    ]

    # negative_examples = list(open(negative_data_file, "r").readlines())
    negative_examples = [[[[1], [random.random()]] * 150] * 70 for _ in range(200)]

    # Split by words
    # x_text = positive_examples + negative_examples
    # x_text = [clean_str(sent) for sent in x_text]

    # Generate labels
    positive_labels = [[0, 1] for _ in range(200)]
    negative_labels = [[1, 0] for _ in range(200)]

    x = np.concatenate([positive_examples, negative_examples], 0)
    y = np.concatenate([positive_labels, negative_labels], 0)

    return [x, y]


def batch_iter(x, y, batch_size, num_epochs, shuffle=True):
    """
    Generates a batch iterator for a dataset.
    """

    data_size = len(x)

    data = np.array(list(zip(x, y)))

    num_batches_per_epoch = int((len(x) - 1) / batch_size) + 1
    for epoch in range(num_epochs):

        # Shuffle the data at each epoch
        if shuffle:
            shuffle_indices = np.random.permutation(np.arange(data_size))
            shuffled_data = data[shuffle_indices]
        else:
            shuffled_data = data

        for batch_num in range(num_batches_per_epoch):
            start_index = batch_num * batch_size
            end_index = min((batch_num + 1) * batch_size, data_size)

            x_list = []
            y_list = []
            for i in range(start_index, end_index):
                x_list.append(shuffled_data[i][0])
                y_list.append(shuffled_data[i][1])

            yield x_list, y_list
