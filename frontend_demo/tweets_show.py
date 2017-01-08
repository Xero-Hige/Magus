import os
from math import ceil

from flask import Flask, render_template, request

PINED_ALERTS_PER_PAGE = 18

app = Flask(__name__)
import json


@app.route('/', methods=["GET", "POST"])
def root():
    tweets = os.listdir("../tweets")
    tweets.sort()
    page = int(request.form.get("PAGE", "0"))

    tweets = [load_tweet(tweets[i]) for i in range(PINED_ALERTS_PER_PAGE * page,
                                       min(PINED_ALERTS_PER_PAGE * (page + 1), len(tweets)))]

    pages = ceil(len(tweets) / PINED_ALERTS_PER_PAGE)

    return render_template("index.html", pagename="Twitter", tweets=tweets, page=page, pages=pages)


def get_tweets(files):
    tweets = []
    for tweet_file_name in files:
        tweet = load_tweet(tweet_file_name)
        tweets.append(tweet)
    return tweets


def load_tweet(tweet_file_name):
    tweet = {}
    with open("../tweets/" + tweet_file_name) as tweet_file:
        tweet_dump = tweet_file.read()
    loaded_tweet = json.loads(tweet_dump, encoding="utf-8")

    tweet["tweet_id"] = tweet_file_name.replace(".json","")
    tweet["tweet_text"] = loaded_tweet.get("text", "")
    tweet["tweet_lang"] = loaded_tweet.get("lang", "")
    if (tweet.get("place")):
        tweet["tweet_place"] = loaded_tweet.get("place", {}).get("name", "")
    else:
        tweet["tweet_place"] = ""
    tweet["tweet_user_lang"] = loaded_tweet.get("user", {}).get("lang", "")
    tweet["tweet_hashtags"] = []
    for hashtag in loaded_tweet.get("entities", {}).get("hashtags", []):
        tweet["tweet_hashtags"].append(hashtag.get("text", ""))
    tweet["tweet_mentions"] = 0
    for x in loaded_tweet.get("entities", {}).get("user_mentions", []):
        tweet["tweet_mentions"] += 1
    tweet["tweet_media"] = {}
    if (loaded_tweet.get("extended_entities")):
        media = loaded_tweet.get("extended_entities", {}).get("media", [])
        for m in media:
            tweet["tweet_media"][m["type"]] = tweet["tweet_media"].get(m["type"], 0) + 1
    return tweet
