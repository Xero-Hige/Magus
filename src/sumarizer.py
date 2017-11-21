import json
import os

from libs.lexicon import Lexicon
from libs.string_generalizer import strip_accents
from libs.tweet_anonymize import full_anonymize_tweet
from libs.tweet_parser import TweetParser

lexicon = Lexicon("lexicons/es_lexicon.lx", "es")
downloaded = 0

for folder, _, filenames in os.walk("results"):

    try:
        batch, emotion, clasification = folder.split("/")[-3:]
    except Exception as e:
        print(folder)
        continue

    words = {}
    values = {}

    for filename in filenames:
        file_path = os.path.join(folder, filename)

        with open(file_path) as input_file:
            parsed_tweet = json.loads(input_file.read())

        if not parsed_tweet:
            print(file_path)

        text = full_anonymize_tweet(parsed_tweet[TweetParser.TWEET_TEXT].lower())

        tag, value = lexicon.auto_tag_sentence(text)

        text = "".join([x if x.isalnum() else ' ' for x in strip_accents(text)])

        text_words = text.split()

        values[value] = values.get(value, 0) + 1

        for word in text_words:
            words[word] = words.get(word, 0) + 1

    with open("evaluation/Result {}_{}_{}".format(batch, emotion, clasification), 'w') as output:
        output.write(json.dumps(values))

    with open("evaluation/Words {}_{}_{}".format(batch, emotion, clasification), 'w') as output:
        for word in words:
            output.write("{} ".format(word) * words[word])
            output.write("\n")
