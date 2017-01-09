import os
import re
from math import ceil

from flask import Flask, render_template, request

PINED_ALERTS_PER_PAGE = 18

app = Flask(__name__)
import json

REMOJIS = re.compile(u"("
                     u"(\ud83d[\ude00-\ude4f])|"  # emoticons
                     u"(\ud83c[\udf00-\uffff])|"  # symbols & pictographs (1 of 2)
                     u"(\ud83d[\u0000-\uddff])|"  # symbols & pictographs (2 of 2)
                     u"(\ud83d[\ude80-\udeff])|"  # transport & map symbols
                     u"(\ud83c[\udde0-\uddff])"  # flags (iOS)
                     u"+"
                     u")", flags=re.UNICODE)

EMOJIS = re.compile(u"\\ud83d", re.UNICODE)

print (EMOJIS)

@app.route('/', methods=["GET", "POST"])
def root():
    tweets = os.listdir("../tweets")
    tweets.sort()
    page = int(request.form.get("PAGE", "0"))

    pages = ceil(len(tweets) / PINED_ALERTS_PER_PAGE)

    tweets = [load_tweet(tweets[i]) for i in range(PINED_ALERTS_PER_PAGE * page,
                                                   min(PINED_ALERTS_PER_PAGE * (page + 1), len(tweets)))]

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

    tweet["tweet_id"] = tweet_file_name.replace(".json", "")
    tweet["tweet_text"] = loaded_tweet.get("text", "")

    print (re.findall(EMOJIS, tweet["tweet_text"]))
    tweet["tweet_text"] = re.sub(EMOJIS, r'<span class="emoji" data-emoji="\1"></span>', tweet["tweet_text"])

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
