import os

from libs.tweet_parser import TweetParser


class TrainSentenceGenerator():
    def __init__(self, dirs, tokenizer):
        self.dirs = dirs
        self.tokenizer = tokenizer

    def __iter__(self):
        for directory in self.dirs:
            for tweet_file in os.walk(directory):
                path = os.path.join(directory, tweet_file)
                tweet = TweetParser.parse_from_json_file(path)
                yield self.tokenizer.tokenize(tweet)
