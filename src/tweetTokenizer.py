#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

from __future__ import absolute_import, print_function, unicode_literals

import re

from KafkaBroker import KafkaReader


class Tokenizer(object):
    def __init__(self):
        pass

    def tokenize(self, text):
        tokens = {}

        text = self.__remove_usernames(text)

        text = self.__remove_urls(text)

        nonAlpha = self.get_non_alphas(text)

        for c in nonAlpha:
            text = text.replace(c, " ")
            tokens[c] = nonAlpha[c]

        keys = sorted(nonAlpha.keys())

        for i in range(len(keys)):
            for j in range(i + 1, len(keys)):
                token = (keys[i], keys[j])

                if not token[0] or not token[1]:
                    continue

                count = tokens.get(token, 0)
                tokens[token] = count + 1

        splited = text.lower().split()

        self.add_ordered_words(splited, tokens)

        self.add_upercase_words(text, tokens)

        return tokens

    def add_upercase_words(self, text, tokens):
        for word in text.split():
            if word.isupper() or word.istitle():
                token = word.upper()
                count = tokens.get(token, 0)
                tokens[token] = count + 1

    def add_ordered_words(self, splited, tokens):
        for i in range(len(splited) - 1):
            for j in range(i + 1, len(splited)):
                token = (splited[i], splited[j])

                if not token[0] or not token[1]:
                    continue

                count = tokens.get(token, 0)
                tokens[token] = count + 1

    def __remove_urls(self, text):
        for url in re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text):
            text = text.replace(url, " URL ")
        return text

    def get_non_alphas(self, text):
        nonAlpha = {}
        for c in text:
            if c.isalpha() or c.isdigit() or c == " " or c == "\n":
                continue

            count = nonAlpha.get(c, 0)
            nonAlpha[c] = count + 1
        return nonAlpha

    def __remove_usernames(self, text):
        for word in text.split():
            if len(word) > 1 and word[0] == '@' and word[1].isalpha():
                text = text.replace(word, " USER ")
        return text


def main():
    t = Tokenizer()
    reader = KafkaReader(b'parsedTweets')

    total = {}

    while True:
        tweet = reader.read()

        if not tweet:
            break

        dict = t.tokenize(tweet["text"])

        for token in dict:
            total[token] = 1

        if dict:
            print(len(total), end="\n\n---\n\n")


if __name__ == '__main__':
    main()
