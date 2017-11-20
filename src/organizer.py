import os
import shutil
from src.libs.tweet_parser import TweetParser

HOUR_SLICE = 30

def sort_tweets(source_folder,target_folder):
    for tweet_file in os.listdir(source_folder):
        tweet = TweetParser.parse_from_json_file(source_folder+"/"+tweet_file)
        month,day,time = tweet["publish_date"]
        hour,minutes,seconds = [int(x) for x in time.split(":")]
        minutes = (minutes // HOUR_SLICE) * HOUR_SLICE

        batch_folder = "{} {} {:02}-{:02}".format(month,day,hour,minutes)

        directory = os.path.join(target_folder,batch_folder)

        if not os.path.exists(directory):
            os.makedirs(directory)

        shutil.move(os.path.join(source_folder,tweet_file),os.path.join(directory,tweet_file))

sort_tweets("./bulk","./sorted")
