import csv
import re

from libs.string_generalizer import strip_accents


class Lexicon():
    ANGER = "anger"
    ANTICIPATION = "anticipation"
    DISGUST = "disgust"
    FEAR = "fear"
    JOY = "joy"
    SADNESS = "sadness"
    SURPRISE = "surprise"
    TRUST = "trust"
    NEUTRAL = "neutral"
    UNDETERMINED = "undetermined"

    _POSITIVE = "positive"
    _NEGATIVE = "negative"

    EMOTIONS = {
        ANGER: 0,
        ANTICIPATION: 1,
        DISGUST: 2,
        FEAR: 3,
        JOY: 4,
        SADNESS: 5,
        SURPRISE: 6,
        TRUST: 7,
        _NEGATIVE: 8,
        _POSITIVE: 9
    }

    def __init__(self, lexicon_file, lang):
        self.lexicon = {}
        self.lang = lang

        with open(lexicon_file) as _file:
            reader = csv.reader(_file, delimiter=" ")
            for line in reader:
                word, tag, value = line

                word = strip_accents(word)

                tag_list = self.lexicon.get(word, [0] * 10)
                tag_list[Lexicon.EMOTIONS[tag]] = int(value)
                self.lexicon[word] = tag_list

    def auto_tag_sentence(self, sentence):
        cleaned = "".join([x.lower() if x.isalpha() else " " for x in sentence])
        cleaned = strip_accents(cleaned)

        found = 0
        total = [0] * 10

        for word in self.lexicon:
            if word not in cleaned:
                continue

            tag_list = self.lexicon[word]

            mod = re.finditer(word, cleaned)

            for i in range(len(tag_list)):
                total[i] += tag_list[i] * mod

            found += mod

        if found == 0:
            return self.UNDETERMINED, 0

        max_value, max_list = self._get_max_index(total)

        if max_value == 0:
            if tag_list[self.EMOTIONS[self._POSITIVE]] > 0:
                return self.UNDETERMINED, 0
            if tag_list[self.EMOTIONS[self._NEGATIVE]] > 0:
                return self.UNDETERMINED, 0
            return self.NEUTRAL, found

        for k, v in self.EMOTIONS.items():
            if v == max_list[0]:
                return k, total[v]

    @staticmethod
    def _get_max_index(tag_list):

        max_value = 0
        max_list = []
        for i in range(8):
            if tag_list[i] < max_value:
                continue

            if tag_list[i] > max_value:
                max_value = tag_list[i]
                max_list = []

            max_list.append(i)

        return max_value, max_list

    def get_associated_lang(self):
        return self.lang
