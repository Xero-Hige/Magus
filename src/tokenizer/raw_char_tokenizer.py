from tokenizer.base_tokenizer import Tokenizer

WINDOW_SIZE = 3


class RawCharTokenizer(Tokenizer):
    @staticmethod
    def tokenize(tweet, preprocessed_text=""):
        result = []

        tweet_text = tweet["tweet_text"]

        for i in range(len(tweet_text) - WINDOW_SIZE + 1):
            result.append(tweet_text[i:i + WINDOW_SIZE])

        return result

    @staticmethod
    def tokenize_raw(tweet):
        """Returns a list of strings, being each string a token of the given
        parsed tweet. Each token appears in the relative order inside the
        tweet given by the tokenize method. """

        return RawCharTokenizer.tokenize(tweet)
