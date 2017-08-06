import os
import re

from flask import Flask, render_template, request, redirect

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


def get_emotions(sentiment):
    for emotions, stored_sentiment in DYADS.items():
        if stored_sentiment == sentiment:
            return emotions
    return []


TAGGED_BASE = {}


class TaggedTweet():
    def __init__(self):
        self.joy = 0
        self.trust = 0
        self.fear = 0
        self.surprise = 0
        self.sadness = 0
        self.disgust = 0
        self.anger = 0
        self.anticipation = 0

        self.totals = 1


@app.route('/', methods=["GET", "POST"])
def root():
    tweets = os.listdir("../tweets")

    tweet = load_tweet(tweets[0])  # random.choice(tweets))

    return render_template("tweet_catalog.html", pagename="Twitter", tweet=tweet)


@app.route('/add', methods=["POST"])
def classify():
    action = request.form["action"]

    if action == 'skip':
        return redirect("/")

    emotion_a = request.form["a"]
    emotion_b = request.form["b"]
    emotion_c = request.form["c"]
    emotion_d = request.form["d"]

    sentiment = request.form["sentiment"]

    lang = request.form["lang"]

    tweet_id = request.form["tweet_id"]

    print (request.form)

    # TODO: LOCK TAKE
    tweet = TAGGED_BASE.get(tweet_id, TaggedTweet())
    emotions = get_emotions(sentiment)

    tweet.joy += 1 if emotion_a == 'joy' else 0
    tweet.joy += 2 if 'joy' in emotions else 0

    tweet.sadness += 1 if emotion_a == 'sadness' else 0
    tweet.sadness += 2 if 'sadness' in emotions else 0

    tweet.trust += 1 if emotion_b == 'trust' else 0
    tweet.trust += 2 if 'trust' in emotions else 0

    tweet.disgust += 1 if emotion_b == 'disgust' else 0
    tweet.disgust += 2 if 'disgust' in emotions else 0

    tweet.fear += 1 if emotion_c == 'fear' else 0
    tweet.fear += 2 if 'fear' in emotions else 0

    tweet.anger += 1 if emotion_c == 'anger' else 0
    tweet.anger += 2 if 'anger' in emotions else 0

    print (emotion_d, emotion_d == 'surprise')
    tweet.surprise += 1 if emotion_d == 'surprise' else 0
    tweet.surprise += 2 if 'surprise' in emotions else 0
    print (tweet.surprise)

    tweet.anticipation += 1 if emotion_d == 'anticipation' else 0
    tweet.anticipation += 2 if 'anticipation' in emotions else 0

    tweet.totals += 3

    TAGGED_BASE[tweet_id] = tweet
    # TODO: LOCK RELEASE

    return redirect("/")


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

    results = [(get_sentiment(sentiments[i], sentiments[j]), (sentiments[i][0] + sentiments[j][0]) / 2)
               for i in range(len(sentiments))
               for j in range(i + 1, len(sentiments))
               if get_sentiment(sentiments[i], sentiments[j]) != "conflict"
               if sentiments[i][0] != 0 and sentiments[j][0] != 0
               ] + [("-", 0)] * 5

    results.sort(reverse=True, key=lambda x: x[1])

    tweet["sentiments"] = results[:5]

    return tweet


def tweet_add_sentiments(tweet):
    _tweet = TAGGED_BASE.get(tweet['tweet_id'], TaggedTweet())

    sentiments = [(_tweet.joy / _tweet.totals, "joy"),
                  (_tweet.trust / _tweet.totals, "trust"),
                  (_tweet.fear / _tweet.totals, "fear"),
                  (_tweet.surprise / _tweet.totals, "surprise"),
                  (_tweet.sadness / _tweet.totals, "sadness"),
                  (_tweet.disgust / _tweet.totals, "disgust"),
                  (_tweet.anger / _tweet.totals, "anger"),
                  (_tweet.anticipation / _tweet.totals, "anticipation")]

    tweet["joy"] = sentiments[0][0]
    tweet["trust"] = sentiments[1][0]
    tweet["fear"] = sentiments[2][0]
    tweet["surprise"] = sentiments[3][0]
    tweet["sadness"] = sentiments[4][0]
    tweet["disgust"] = sentiments[5][0]
    tweet["anger"] = sentiments[6][0]
    tweet["anticipation"] = sentiments[7][0]

    return sentiments


def get_sentiment(sentiment_a, sentiment_b):
    if not (sentiment_a[1], sentiment_b[1]) in DYADS:
        return DYADS.get((sentiment_b[1], sentiment_a[1]), "conflict")
    else:
        return DYADS.get((sentiment_a[1], sentiment_b[1]), "conflict")
