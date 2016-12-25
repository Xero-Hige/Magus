# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

import pickle as Serializer
import re
import string
import sys

from RabbitHandler import *

STOP_LISTS = ["arabic", "chinese", "english", "german", "japanese", "portugese", "spanish"]


class TweetProcesser():
    ''' '''

    def __init__(self):
        self.stopwords = {}
        for f in STOP_LISTS:
            with open("stopwords/" + f, 'r', encoding="utf-8") as stopword_list:
                for line in stopword_list:
                    line.rstrip()
                    self.stopwords[line] = 0

    def _is_stopword(self, word):
        return word in self.stopwords

    @staticmethod
    def _is_junk(token):
        if token in string.whitespace:
            return True

        if token.isdigit():
            return True

        return len(token) < 2 and (token in string.punctuation or token in string.ascii_letters)

    @staticmethod
    def __remove_urls(text):
        for url in re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text):
            text = text.replace(url, " URL ")
        return text

    @staticmethod
    def __remove_usernames(text):
        for word in text.split():
            if len(word) > 1 and word[0] == '@' and word[1].isalpha():
                text = text.replace(word, " USER ")
        return text

    @staticmethod
    def __transform_hashtags(text):
        for word in text.split():
            if len(word) > 1 and word[0] == '#' and word[1].isalpha():
                text = text.replace(word, " HTAG" + word[1:] + " ")
        return text

    def process(self, tweet_dict):
        text = tweet_dict["text"]

        text = self.__remove_usernames(text)
        text = self.__remove_urls(text)
        text = self.__transform_hashtags(text)

        text_list = [word for word in text.split() if not self._is_junk(word) and not self._is_stopword(word)]

        text = " ".join(text_list)
        tweet_dict["processed_text"] = text

        text_list = [word for word in text_list if word and word != "URL" and word != "USER" and word[:4] != "HTAG"]
        text = " ".join(text_list)
        tweet_dict["cleaned_text"] = text

def main(argv):
    debug = False
    worker = 0
    if len(argv) > 1:
        debug = True
        worker = argv[1]

    tsp = TweetProcesser()
    reader = RabbitHandler("parsed_tweets")
    writer = RabbitHandler("processed_tweets")

    def callback(tweet):
        if not tweet:
            return

        tweet = Serializer.loads(tweet)

        tsp.process(tweet)

        if debug:
            print("Worker [", worker, "] ", tweet["text"])
            sys.stdout.flush()

        writer.send_message(Serializer.dumps(tweet))

    reader.receive_messages(callback)


if __name__ == '__main__':
    main(sys.argv)
