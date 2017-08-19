import random
import re
from subprocess import Popen, PIPE

from flask import Flask, render_template, request, redirect

from tweets_db import *
from tweets_db import DB_Handler

app = Flask(__name__)
import json

EMOJIS = re.compile(u"\\ud83d", flags=re.UNICODE)

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

GROUPS = {
    "love": "happy",
    "alarm": "angry",
    "disappointment": "sad",
    "remorse": "sad",
    "contempt": "angry",
    "agression": "angry",
    "optimism": "happy",
    "guilt": "sad",
    "despair": "sad",
    "envy": "angry",
    "cynism": "angry",
    "pride": "happy",
    "fatalism": "sad",
    "delight": "happy",
    "sentimentality": "sad",
    "shame": "sad",
    "outrage": "angry",
    "pessimism": "sad",
    "anxiety": "angry"
}


def totalize_groups(sentiments):
    total = {"happy": 0, "sad": 0, "angry": 0, "none": 0}
    acum = 0

    for sentiment in sentiments:
        total[GROUPS.get(sentiment[0], "none")] += sentiment[1]
        acum += sentiment[1]

    if acum == 0:
        return total

    for sentiment in total:
        total[sentiment] /= acum
        total[sentiment] *= 100

    return total


def get_emotions(sentiment):
    for emotions, stored_sentiment in DYADS.items():
        if stored_sentiment == sentiment:
            return emotions
    return []


@app.route('/classify', methods=["GET"])
def classify_get():
    tweets = os.listdir("../tweets")

    tweet = load_tweet(random.choice(tweets))

    return render_template("tweet_catalog.html", tweet=tweet)


@app.route('/', methods=["GET"])
def root():
    with open("../tweets/something", 'w') as kaiser:
        kaiser.write("thing")

    return render_template("index.html")


@app.route('/add', methods=["GET"])
def adder_get():
    return render_template("tweet_adder.html")


@app.route('/add', methods=["POST"])
def adder_post():
    action = request.form["action"]

    if action == 'skip':
        return redirect("/classify")

    tweet_id = request.form["tweet_id"]

    p = Popen(["python3", "tweets_downloader.py"], stdout=PIPE, stdin=PIPE, stderr=PIPE, cwd='../')
    stdout_data = p.communicate(input=str.encode('{}\n'.format(tweet_id)))[0]
    print ("DEBUG", stdout_data)
    if "Error" in str(stdout_data):
        return redirect("/add")

    p = Popen(["ruby", "uploader.rb", "tweets/{}.json".format(tweet_id), "'../tweets/{}.json'".format(tweet_id)])
    stdout_data = p.communicate(input=b'\n')
    print ("DEBUG", stdout_data)

    classify_tweet()

    return redirect("/add")


def classify_tweet():
    emotion_a = request.form["a"]
    emotion_b = request.form["b"]
    emotion_c = request.form["c"]
    emotion_d = request.form["d"]
    sentiment = request.form["sentiment"]
    lang = request.form["lang"]
    tweet_id = request.form["tweet_id"]
    with DB_Handler() as handler:
        # TODO: LOCK TAKE
        tweet = handler.get_tagged(tweet_id)
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

        tweet.totals += 3 if tweet.totals != 1 else 2
        # TODO: LOCK RELEASE


@app.route('/classify', methods=["POST"])
def classify():
    action = request.form["action"]

    if action == 'skip':
        return redirect("/classify")

    classify_tweet()

    return redirect("/classify")


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

    tweet["tweet_text"] = re.sub(EMOJIS, r'\<span class="emoji" data-emoji="\g<0>"\>\</span\>', tweet["tweet_text"])

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
    tweet["groups"] = totalize_groups(results)

    return tweet


def tweet_add_sentiments(tweet):
    with DB_Handler() as handler:
        _tweet = handler.get_tagged(tweet['tweet_id'])

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


if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
