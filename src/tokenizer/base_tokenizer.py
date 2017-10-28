class Tokenizer():
    """Defines a tokenizer class to parse tweets"""

    @staticmethod
    def preprocess(tweet):
        """Preprocess the tweet to be in the format to use the tokenizer. It
        only should be used in the trainer."""

        raise NotImplementedError

    @staticmethod
    def tokenize(tweet):
        """Returns a list of strings, being each string a token of the given
        parsed tweet. Each token appears in the relative order inside the
        tweet given by the tokenize method"""

        raise NotImplementedError

    @staticmethod
    def tokenize_raw(tweet):
        """Returns a list of strings, being each string a token of the given
        parsed tweet. Each token appears in the relative order inside the
        tweet given by the tokenize method. It preprocess and tokenizes tweet, so
        the arg tweet is modified."""

        raise NotImplementedError
