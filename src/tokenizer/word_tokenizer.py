from libs.tweet_anonymize import full_anonymize_tweet
from tokenizer.base_tokenizer import Tokenizer


class WordTokenizer(Tokenizer):
    @staticmethod
    def preprocess(tweet):
        tweet["tweet_text"] = tweet["tweet_text"].lower()
        tweet["tweet_text"] = full_anonymize_tweet(tweet["tweet_text"])

    @staticmethod
    def tokenize(tweet):
        return [word for word in tweet["tweet_text"].split()]

    @staticmethod
    def tokenize_raw(tweet):
        """Returns a list of strings, being each string a token of the given
        parsed tweet. Each token appears in the relative order inside the
        tweet given by the tokenize method. It preprocess and tokenizes tweet, so
        the arg tweet is modified."""

        WordTokenizer.preprocess(tweet)
        return WordTokenizer.tokenize(tweet)
