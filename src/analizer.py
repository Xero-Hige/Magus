import json
import os
import random

from libs.lexicon import Lexicon
from libs.tweet_parser import TweetParser

lexicon = Lexicon("lexicons/es_lexicon.lx", "es")

MAX_PER_ITERATION = 20

for batch in range(1, 5):
    for folder, _, files in os.walk("../tweets_autotaged/tweets_bashfull_{}".format(batch)):

        random.shuffle(files)

        emotion = folder.split("/")[-1]

        print("\n\nValidate --> {}\n\n".format(emotion))

        added = 0
        for _file in files:
            if added > MAX_PER_ITERATION:
                break

            tweet_id = _file.split(".")[0]
            output_dir = os.path.join(".", "results", "batch{}".format(batch), emotion)

            with open(os.path.join(folder, _file)) as input_file:
                raw_tweet = json.loads(input_file.read())

            tweet = TweetParser.parse_from_dict(raw_tweet)

            key_pressed = ""
            while key_pressed not in ["y", "n", "s"]:
                key_pressed = input("\n\t<{}>:\n{}\n\nY/N".format(emotion, tweet[TweetParser.TWEET_TEXT]))

            if key_pressed == "y":
                output_dir = os.path.join(output_dir, "good")
                try:
                    os.makedirs(output_dir)
                except:
                    pass

            elif key_pressed == "n":
                output_dir = os.path.join(output_dir, "bad")
                try:
                    os.makedirs(output_dir)
                except:
                    pass

            else:
                continue

            out_path = os.path.join(output_dir, "{}.json".format(tweet_id))
            with open(out_path, 'w') as out_file:
                out_file.write(json.dumps(raw_tweet))

            os.remove(os.path.join(folder, _file))
            added += 1
