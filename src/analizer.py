import os
import random

from libs.lexicon import Lexicon
from libs.tweet_parser import TweetParser

lexicon = Lexicon("lexicons/es_lexicon.lx", "es")

for folder, _, files in os.walk("./tweets_bashfull_old"):
    random.shuffle(files)

    emotion = folder.split("/")[-1]
    print("Validate --> {}".format(emotion))

    batch = 1

    for _file in files[:10]:
        tweet_id = _file.split(".")[0]
        output_dir = os.path.join(".", "results", "batch{}".format(batch))

        tweet = TweetParser.parse_from_json_file(os.path.join(folder, _file))

        key_pressed = input("{}: {}  Y/N".format(tweet_id, tweet[TweetParser.TWEET_TEXT]))

        if key_pressed == "y":
            output_dir = os.path.join(output_dir, "good")
            try:
                os.makedirs(output_dir)
            except:
                pass
            print(output_dir + "{}.json".format(tweet_id))

        elif key_pressed == "n":
            output_dir = os.path.join(output_dir, "bad")
            try:
                os.makedirs(output_dir)
            except:
                pass
            print(output_dir + "{}.json".format(tweet_id))

        else:
            print("BOBO")

        print("<<{}>> {}".format(emotion, tweet_id))
