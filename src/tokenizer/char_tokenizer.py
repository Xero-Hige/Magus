WINDOW_SIZE = 3

class Tokenizer():

    @staticmethod
    def tokenize(tweet):
        result = []

        tweet_text = tweet["tweet_text"]

        for i in range(len(tweet_text)-WINDOW_SIZE):
            result.append(tweet_text[i:i+WINDOW_SIZE])

        return result
