import os

from libs.tweet_parser import TweetParser


class TrainSentenceGenerator():
    def __init__(self, dirs, tokenizer):
        self.dirs = dirs
        self.tokenizer = tokenizer

    def __iter__(self):
        for directory in self.dirs:
            for _, _, tweet_files in os.walk(directory):
                for tweet_file in tweet_files:
                    path = os.path.join(directory, tweet_file)
                    tweet = TweetParser.parse_from_json_file(path)
                    tweet["tweet_text"] = tweet["tweet_text"].lower()
                    yield self.tokenizer.tokenize(tweet)
