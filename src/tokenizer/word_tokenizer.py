from base_tokenizer import Tokenizer
from libs.tweet_anonymize import full_anonymize_tweet


class WordTokenizer(Tokenizer):
    @staticmethod
    def preprocess(tweet):
        tweet["tweet_text"] = tweet["tweet_text"].lower()
        tweet["tweet_text"] = full_anonymize_tweet(tweet["tweet_text"])

    @staticmethod
    def tokenize(tweet):
        return [word for word in tweet["tweet_text"].split()]
