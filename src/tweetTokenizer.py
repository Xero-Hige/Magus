#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

import pickle as Serializer
import re
import string
import sys

from RabbitHandler import *

STOP_LISTS = ["arabic", "chinese", "english", "german", "japanese", "portugese", "spanish"]


class Tokenizer(object):
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

    def tokenize(self, text):
        tokens = {}

        text = self.__remove_usernames(text)

        text = self.__remove_urls(text)

        text = self.__transform_hashtags(text)

        non_alpha = self.get_non_alphas(text)

        for c in non_alpha:
            text = text.replace(c, " ")
            tokens[c] = non_alpha[c]

        keys = sorted(non_alpha.keys())

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

    @staticmethod
    def add_upercase_words(text, tokens):
        for word in text.split():
            if word.isupper() or word.istitle() and not word[:4] == "HTAG":
                token = word.upper()
                count = tokens.get(token, 0)
                tokens[token] = count + 1

            if word.isupper() or word.istitle() and word[:4] == "HTAG":
                token = word[4:].lower()
                count = tokens.get(token, 0)
                tokens[token] = count + 1

            if word.isdigit():
                count = tokens.get(word, 0)
                tokens[word] = count + 1

    def add_ordered_words(self, splited, tokens):
        for i in range(len(splited) - 1):
            for j in range(i + 1, len(splited)):
                token = (splited[i], splited[j])

                if token in tokens:
                    tokens[token] += 1

                if not token[0] or not token[1]:
                    continue

                # if len(token[0])<2 or len(token[1])<2:
                #    continue

                # if len(token[0])<3 and len(token[1])<3:
                #    continue

                if self._is_junk(token[0]) or self._is_junk(token[1]):
                    continue

                if self._is_stopword(token[0]) and self._is_stopword(token[1]):
                    continue

                tokens[token] = 1

    @staticmethod
    def __remove_urls(text):
        for url in re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text):
            text = text.replace(url, " URL ")
        return text

    @staticmethod
    def get_non_alphas(text):
        nonAlpha = {}
        for c in text:
            if c.isalpha() or c.isdigit() or c == " " or c == "\n" or c == '' or c == "'":
                continue

            count = nonAlpha.get(c, 0)
            nonAlpha[c] = count + 1
        return nonAlpha

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


def selectTokens(unclass):
    tags = {}
    tokens = {}
    tokens_totals = {}

    for tag, tag_tokens in unclass:
        tags[tag] = tags.get(tag, 0) + 1
        for token in tag_tokens:
            tokens[token] = tokens.get(token, {})
            tokens[token][tag] = tokens[token].get(tag, 0) + 1
            tokens_totals[token] = tokens_totals.get(token, 0) + 1

    results = {}

    for tag in tags.keys():
        for token in tokens.keys():
            results[(tag, token)] = (tokens.get(token, {}).get(tag, 0)) / (tags.get(tag, 1))

    prom = {}

    for tag in tags.keys():
        for token in tokens.keys():
            prom[token] = prom.get(token, 0) + results[(tag, token)]

    selected = []

    while len(unclass) > 0:
        infogainer = []
        for tag in tags.keys():
            for token in tokens.keys():
                # prom[token] = prom.get(token,0) + results[(tag,token)]
                result = results[(tag, token)] / prom[token]
                if result == 0:
                    continue
                infogainer.append((result, (tag, token)))

        if len(infogainer) < 1:
            break

        infogainer.sort(key=lambda x: -x[0])
        # print(infogainer)
        gain, key = infogainer[0]
        tag, token = key

        # print("\n\n\n", tag, "---", token, "\n\n\n")
        selected.append(token)
        tokens.pop(token)
        # print(selected)
        #
        # print("\n\nLEN:", len(unclass), "\n\n")
        # print(tag)
        newUnclass = []
        for x in unclass:
            if (x[0] == tag and token in x[1]):
                for tok in x[1]:
                    if token == tok:
                        continue
                    if not tok in tokens:
                        # print(tok)
                        continue
                    tokens[tok][tag] = max(0, tokens.get(tok, {}).get(tag, 0) - 1)
                    tokens_totals[tok] -= 1
                continue
            newUnclass.append(x)
            # list(filter(lambda x: x[0]!=tag,unclass))

        unclass = newUnclass
        # for x in unclass:
        #    print(x[0],x[0] == tag,tag)
        # print (unclass)
        print("\n\nLEN:", len(unclass), "\n\n")

        tags[tag] = 0

        for t, l in unclass:
            if t == tag:
                tags[tag] += 1

        for token_ in tokens.keys():
            try:
                results[(tag, token_)] = (tokens.get(token_, {}).get(tag, 0)) / (tags.get(tag, 1))
            except ZeroDivisionError:
                results[(tag, token_)] = 0

    return tags.keys(), selected


def main():
    t = Tokenizer()

    reader = RabbitHandler("parsed_tweets")

    def callback(tweet):

        if not tweet:
            return

        tweet = Serializer.loads(tweet)

        dict = t.tokenize(tweet["text"])

        tag = tweet.get("country", None)
        print(len(dict))
        sys.stdout.flush()

        if not tag:
            return

            # unclass.append((tag, dict))


            # if len(unclass) > 1000:
            #    print("Calculando")
            #    tags, selected = selectTokens(unclass)
            #    print("Tags:", tag)
            #    print("Selected:", selected)
            #    print("Len Selected:", len(selected))

            #
            # pre = len(total)
            #
            # for token in dict:
            #     total[token] = 1
            #
            # post = len(total)
            #
            # if dict:
            #     print(len(total), end="\n\n--New("+str(post-pre)+")--\n\n")

            # if (post-pre)>20:
            # print(dict.keys(),end="\n\n___\n---\n\n")
            # with open("tokens.tkn",'a') as tokens:
            # tokens.writelines([str(x)+"\n" for x in total.keys()])
            # tokens.write(str(i)+","+str(post-pre)+"\n")

    reader.receive_messages(callback)


if __name__ == '__main__':
    main()
