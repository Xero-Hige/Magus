from tokenizer.base_tokenizer import Tokenizer

from libs.tweet_anonymize import full_anonymize_tweet

WINDOW_SIZE = 3


class CharTokenizer(Tokenizer):
    @staticmethod
    def preprocess(tweet):
        tweet["tweet_text"] = tweet["tweet_text"].lower()
        tweet["tweet_text"] = full_anonymize_tweet(tweet["tweet_text"])

    @staticmethod
    def tokenize(tweet):
        result = []

        tweet_text = tweet["tweet_text"]

        for i in range(len(tweet_text) - WINDOW_SIZE + 1):
            result.append(tweet_text[i:i + WINDOW_SIZE])

        return result
