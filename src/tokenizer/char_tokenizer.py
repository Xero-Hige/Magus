from libs.tweet_anonymize import full_anonymize_tweet
from tokenizer.base_tokenizer import Tokenizer

WINDOW_SIZE = 3


class CharTokenizer(Tokenizer):
    @staticmethod
    def _text_preprocess(tweet):
        preprocessed_text = tweet["tweet_text"].lower()
        return full_anonymize_tweet(preprocessed_text)

    @staticmethod
    def tokenize(tweet, preprocessed_text=None):
        result = []

        tweet_text = preprocessed_text if preprocessed_text else tweet["tweet_text"]

        for i in range(len(tweet_text) - WINDOW_SIZE + 1):
            result.append(tweet_text[i:i + WINDOW_SIZE])

        return result

    @staticmethod
    def tokenize_raw(tweet):
        """Returns a list of strings, being each string a token of the given
        parsed tweet. Each token appears in the relative order inside the
        tweet given by the tokenize method. """

        preprocessed_text = CharTokenizer._text_preprocess(tweet)
        return CharTokenizer.tokenize(tweet, preprocessed_text)
