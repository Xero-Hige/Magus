import os
import random
import re

from flask import Flask, render_template

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

DYADS = {
    ("joy", "trust"): "love",
    ("trust", "fear"): "submission",
    ("fear", "surprise"): "alarm",
    ("surprise", "sadness"): "disappointment",
    ("sadness", "disgust"): "remorse",
    ("disgust", "anger"): "contempt",
    ("anger", "anticipation"): "agression",
    ("anticipation", "joy"): "optimism",
    ("joy", "fear"): "guilt",
    ("trust", "surprise"): "curiosity",
    ("fear", "sadness"): "despair",
    ("sadness", "anger"): "envy",
    ("disgust", "anticipation"): "cynism",
    ("joy", "anger"): "pride",
    ("trust", "anticipation"): "fatalism",
    ("joy", "surprise"): "delight",
    ("trust", "sadness"): "sentimentality",
    ("fear", "disgust"): "shame",
    ("surprise", "anger"): "outrage",
    ("sadness", "anticipation"): "pessimism",
    ("joy", "disgust"): "morbidness",
    ("trust", "anger"): "dominance",
    ("fear", "anticipation"): "anxiety"
}


@app.route('/', methods=["GET", "POST"])
def root():
    tweets = os.listdir("../tweets")
    random.shuffle(tweets)
    tweets = [load_tweet(tweets[i]) for i in range(10)]

    return render_template("tweet_catalog.html", pagename="Twitter", tweets=tweets)


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

    tweet["tweet_text"] = re.sub(EMOJIS, r'<span class="emoji" data-emoji="\1"></span>', tweet["tweet_text"])

    tweet["tweet_lang"] = loaded_tweet.get("lang", "")

    if tweet.get("place"):
        tweet["tweet_place"] = loaded_tweet.get("place", {}).get("name", "")
    else:
        tweet["tweet_place"] = ""

    tweet["tweet_user_lang"] = loaded_tweet.get("user", {}).get("lang", "")

    tweet["tweet_hashtags"] = []
    for hashtag in loaded_tweet.get("entities", {}).get("hashtags", []):
        tweet["tweet_hashtags"].append(hashtag.get("text", ""))

    tweet["tweet_mentions"] = 0
    for _ in loaded_tweet.get("entities", {}).get("user_mentions", []):
        tweet["tweet_mentions"] += 1

    tweet["tweet_media"] = {}
    if loaded_tweet.get("extended_entities"):
        media = loaded_tweet.get("extended_entities", {}).get("media", [])
        for m in media:
            tweet["tweet_media"][m["type"]] = tweet["tweet_media"].get(m["type"], 0) + 1

    sentiments = tweet_add_sentiments(tweet)

    sentiments.sort(reverse=True)

    sentiments = sentiments[:3]

    results = [(get_sentiment(sentiments[0], sentiments[1]), (sentiments[0][0] + sentiments[1][0]) / 2),
               (get_sentiment(sentiments[1], sentiments[2]), (sentiments[1][0] + sentiments[2][0]) / 2),
               (get_sentiment(sentiments[0], sentiments[2]), (sentiments[0][0] + sentiments[2][0]) / 2)]

    tweet["sentiments"] = results

    return tweet


def tweet_add_sentiments(tweet):
    tweet["joy"] = random.random() * 100
    tweet["trust"] = random.random() * 100
    tweet["fear"] = random.random() * 100
    tweet["surprise"] = random.random() * 100
    tweet["sadness"] = 100 - tweet["joy"]
    tweet["disgust"] = 100 - tweet["trust"]
    tweet["anger"] = 100 - tweet["fear"]
    tweet["anticipation"] = 100 - tweet["surprise"]
    sentiments = [(tweet["joy"], "joy"),
                  (tweet["trust"], "trust"),
                  (tweet["fear"], "fear"),
                  (tweet["surprise"], "surprise"),
                  (tweet["sadness"], "sadness"),
                  (tweet["disgust"], "disgust"),
                  (tweet["anger"], "anger"),
                  (tweet["anticipation"], "anticipation")]
    return sentiments


def get_sentiment(sentiment_a, sentiment_b):
    if not (sentiment_a[1], sentiment_b[1]) in DYADS:
        return DYADS.get((sentiment_b[1], sentiment_a[1]), "conflict")
    else:
        return DYADS.get((sentiment_a[1], sentiment_b[1]), "conflict")
