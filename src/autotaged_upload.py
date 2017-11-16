import csv
import json
import math
import os

from libs.db_tweet import DB_Handler
from libs.tweet_parser import TweetParser

for _dir in os.listdir("strings"):
    with open("strings/" + _dir) as _file:
        writer = csv.reader(_file)

        for line in writer:
            t_id, tweet_class, annotation, text = line

            t_id = "f" + t_id
            tweet_class = tweet_class.lower()
            annotation = (math.ceil(10 * float(annotation)))
            print(t_id, tweet_class, annotation)

            base = json.loads(open("base_tweet.json").read())

            base["text"] = text
            base["lang"] = "en"
            base["user"]["lang"] = "en"
            base["id_str"] = t_id

            TweetParser.parse_from_dict(base)

            with open("fakes/{}.json".format(t_id), "w") as _file2:
                _file2.write(json.dumps(base))

            with DB_Handler() as handler:
                tweet = handler.get_tagged(t_id)

                if tweet_class == "joy" or tweet_class == "love" or tweet_class == "optimism":
                    tweet.joy = annotation
                if tweet_class == "trust" or tweet_class == "love" or tweet_class == "submission":
                    tweet.trust = annotation
                if tweet_class == "fear" or tweet_class == "awe" or tweet_class == "submission":
                    tweet.fear = annotation
                if tweet_class == "surprise" or tweet_class == "awe" or tweet_class == "disapproval":
                    tweet.surprise = annotation
                if tweet_class == "sadness" or tweet_class == "remorse" or tweet_class == "disapproval":
                    tweet.sadness = annotation
                if tweet_class == "disgust" or tweet_class == "remorse" or tweet_class == "contempt":
                    tweet.disgust = annotation
                if tweet_class == "anger" or tweet_class == "aggression" or tweet_class == "contempt":
                    tweet.anger = annotation
                if tweet_class == "anticipation" or tweet_class == "aggression" or tweet_class == "optimism":
                    tweet.anticipation = annotation

                tweet.totals = annotation
