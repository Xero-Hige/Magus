from base_tokenizer import Tokenizer


class WordTokenizer(Tokenizer):
    @staticmethod
    def tokenize(tweet):
        return [word for word in tweet["tweet_text"].split()]
