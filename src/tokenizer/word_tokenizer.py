from libs.string_generalizer import strip_accents
from libs.text_reducer import reduce_text
from libs.tweet_anonymize import full_anonymize_tweet
from tokenizer.base_tokenizer import Tokenizer


class WordTokenizer(Tokenizer):
    @staticmethod
    def _text_preprocess(tweet):
        preprocessed_text = tweet["tweet_text"].lower()
        preprocessed_text = full_anonymize_tweet(preprocessed_text)
        preprocessed_text = reduce_text(preprocessed_text)
        return strip_accents(preprocessed_text)

    @staticmethod
    def tokenize(tweet, preprocessed_text=""):
        tweet_text = preprocessed_text if preprocessed_text else tweet["tweet_text"]
        return [word for word in tweet_text.split()]

    @staticmethod
    def tokenize_raw(tweet):
        """Returns a list of strings, being each string a token of the given
        parsed tweet. Each token appears in the relative order inside the
        tweet given by the tokenize method."""

        preprocessed_text = WordTokenizer._text_preprocess(tweet)
        return WordTokenizer.tokenize(tweet, preprocessed_text)
