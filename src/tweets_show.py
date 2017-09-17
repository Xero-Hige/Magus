import random
import re
from subprocess import Popen, PIPE

from flask import Flask, render_template, request, redirect

from libs.tweet_parser import TweetParser
from tweet_process import censor_urls, anonymize_usernames
from tweets_db import *
from tweets_db import DB_Handler
from utils.tweets_scrapper import do_scrapping

NONE = "none"
SAD = "sad"
ANGRY = "angry"
HAPPY = "happy"

app = Flask(__name__)

EMOJIS = re.compile(u"\\ud83d", flags=re.UNICODE)

DYADS = {
    ("joy", "trust"): "love",
    ("trust", "fear"): "submission",
    ("fear", "surprise"): "alarm",
    ("surprise", "sadness"): "disappointment",
    ("sadness", "disgust"): "remorse",
    ("disgust", "anger"): "contempt",
    ("anger", "anticipation"): "aggression",
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
    ("fear", "anticipation"): "anxiety",
    (NONE, NONE): NONE
}

GROUPS = {
    "love": HAPPY,
    "optimism": HAPPY,
    "pride": HAPPY,
    "delight": HAPPY,
    "alarm": ANGRY,
    "contempt": ANGRY,
    "aggression": ANGRY,
    "envy": ANGRY,
    "cynism": ANGRY,
    "outrage": ANGRY,
    "anxiety": ANGRY,
    "disappointment": SAD,
    "remorse": SAD,
    "guilt": SAD,
    "despair": SAD,
    "fatalism": SAD,
    "sentimentality": SAD,
    "shame": SAD,
    "pessimism": SAD,
    NONE: NONE
}


def totalize_groups(sentiments):
    total = {HAPPY: 0, SAD: 0, ANGRY: 0, NONE: 0}
    acum = 0

    for sentiment in sentiments:
        total[GROUPS.get(sentiment[0], NONE)] += sentiment[1]
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

    return render_template("tweet_catalog.html", tweet=tweet, max=max)


@app.route('/classify/<int:tweet_id>', methods=["GET"])
def classify_exact_get(tweet_id):
    tweet_id = "{}.json".format(tweet_id)
    tweets = os.listdir("../tweets")

    if str(tweet_id) not in tweets:
        return redirect("/add")

    tweet = load_tweet(tweet_id)

    return render_template("tweet_catalog.html", tweet=tweet, max=max)


@app.route('/', methods=["GET"])
def root():
    return render_template("index.html")


@app.route('/add', methods=["GET"])
def adder_get():
    return render_template("tweet_adder.html")


@app.route('/add', methods=["POST"])
def adder_post():
    action = request.form["action"]

    if action == 'finish':
        return redirect("/")

    tweet_id = request.form["tweet_id"]

    p = Popen(["python3", "tweets_downloader.py"], stdout=PIPE, stdin=PIPE, stderr=PIPE, cwd='./utils')
    stdout_data = p.communicate(input=str.encode('{}\n'.format(tweet_id)))

    if "err" in str(stdout_data).lower():
        print ("DEBUG - Script Error: ", stdout_data)

    p = Popen(["ruby", "uploader.rb", "tweets/{}.json".format(tweet_id), "../tweets/{}.json".format(tweet_id)],
              stdout=PIPE, stdin=PIPE, stderr=PIPE)

    stdout_data = p.communicate(input=b'\n')
    if "err" in str(stdout_data).lower():
        print ("DEBUG - Script Error: ", stdout_data)

    classify_tweet()

    return redirect("/add")


@app.route('/scrapp', methods=['GET'])
def scrapp():
    locations = request.args.get('location', "")
    topics = request.args.get('topics', "")
    geo = request.args.get('geo', "")

    child = os.fork()
    if child == 0:
        p = Popen(["mkdir", "upload"],
                  stdout=PIPE, stdin=PIPE, stderr=PIPE)
        p.communicate(input=b'\n')

        p = Popen(["git", "init"],
                  stdout=PIPE, stdin=PIPE, stderr=PIPE, cwd='./upload')
        p.communicate(input=b'\n')

        p = Popen(["git", "remote", "add", "origin", "https://{}:{}@github.com/Xero-Hige/Magus.git".format(
            os.environ.get('GITHUB_USER', ""),
            os.environ.get('GITHUB_PASS', ""))],
                  stdout=PIPE, stdin=PIPE, stderr=PIPE, cwd='./upload')
        p.communicate(input=b'\n')

        p = Popen(["git", "remote", "update"],
                  stdout=PIPE, stdin=PIPE, stderr=PIPE, cwd='./upload')
        stdout_data = p.communicate(input=b'\n')

        p = Popen(["git", "fetch"],
                  stdout=PIPE, stdin=PIPE, stderr=PIPE, cwd='./upload')
        p.communicate(input=b'\n')

        p = Popen(["git", "checkout", "tweets"],
                  stdout=PIPE, stdin=PIPE, stderr=PIPE, cwd='./upload')
        p.communicate(input=b'\n')

        p = Popen(["git", "pull", "origin", "tweets"],
                  stdout=PIPE, stdin=PIPE, stderr=PIPE, cwd='./upload')
        p.communicate(input=b'\n')

        do_scrapping(locations, topics, geo, "./upload/bulk")

        p = Popen(["git", "add", "bulk"],
                  stdout=PIPE, stdin=PIPE, stderr=PIPE, cwd='./upload')
        p.communicate(input=b'\n')

        p = Popen(["git", "commit", "-m",
                   "New bulk added with Location={} :: Topics={} ".format(locations, topics)],
                  stdout=PIPE, stdin=PIPE, stderr=PIPE, cwd='./upload')
        p.communicate(input=b'\n')

        p = Popen(["git", "push", "--set-upstream", "origin", "tweets"],
                  stdout=PIPE, stdin=PIPE, stderr=PIPE, cwd='./upload')
        stdout_data = p.communicate(
            input=bytes('{}\n{}\n'.format(
                os.environ.get('GITHUB_USER', ""),
                os.environ.get('GITHUB_PASS', "")),
                'utf-8'))

        print ("DEBUG - INFO : ", stdout_data)

        exit(0)
    else:
        return redirect('/')


def classify_tweet():
    dyad_a = request.form["a"]
    dyad_b = request.form["b"]
    dyad_c = request.form["c"]
    dyad_d = request.form["d"]

    is_ironic = request.form["ironic"] == "ironic"

    sentiment = request.form["sentiment"]

    lang = request.form["lang"]
    tweet_id = request.form["tweet_id"]

    with DB_Handler() as handler:
        # TODO: LOCK TAKE
        tweet = handler.get_tagged(tweet_id)

        if dyad_a == dyad_b and dyad_b == dyad_c and dyad_c == dyad_d and dyad_d == NONE:
            tweet.none += 1
        else:
            tweet.joy += 1 if dyad_a == 'joy' else 0
            tweet.sadness += 1 if dyad_a == 'sadness' else 0
            tweet.trust += 1 if dyad_b == 'trust' else 0
            tweet.disgust += 1 if dyad_b == 'disgust' else 0
            tweet.fear += 1 if dyad_c == 'fear' else 0
            tweet.anger += 1 if dyad_c == 'anger' else 0
            tweet.surprise += 1 if dyad_d == 'surprise' else 0
            tweet.anticipation += 1 if dyad_d == 'anticipation' else 0

        if sentiment == NONE:
            tweet.none += 1
        else:
            emotions = get_emotions(sentiment)

            tweet.joy += 2 if 'joy' in emotions else 0
            tweet.sadness += 2 if 'sadness' in emotions else 0
            tweet.trust += 2 if 'trust' in emotions else 0
            tweet.disgust += 2 if 'disgust' in emotions else 0
            tweet.fear += 2 if 'fear' in emotions else 0
            tweet.anger += 2 if 'anger' in emotions else 0
            tweet.surprise += 2 if 'surprise' in emotions else 0
            tweet.anticipation += 2 if 'anticipation' in emotions else 0

        tweet.ironic += 3 if is_ironic else 0

        tweet.totals += 3 if tweet.totals != 1 else 2
        # TODO: LOCK RELEASE


@app.route('/classify', methods=["POST"])
def classify():
    action = request.form["action"]

    if action == 'skip':
        return redirect("/classify")

    classify_tweet()

    return redirect("/classify")


@app.route('/status', methods=["GET"])
def status():
    totals_emotions, totals_groups = get_tweets_status()
    return render_template("DB_status.html", emotions=totals_emotions, groups=totals_groups)


def get_tweets(files):
    tweets = []
    for tweet_file_name in files:
        tweet = load_tweet(tweet_file_name)
        tweets.append(tweet)
    return tweets


def load_tweet(tweet_file_name):
    # with open("../tweets/" + tweet_file_name) as tweet_file:
    #    tweet_dump = tweet_file.read()
    #
    # loaded_tweet = json.loads(tweet_dump, encoding="utf-8")

    tweet = TweetParser.parse_from_json_file("../tweets/" + tweet_file_name)

    tweet["tweet_text"] = anonymize_usernames(censor_urls(tweet.get(TweetParser.TWEET_TEXT, "")))
    tweet["tweet_text"] = re.sub(EMOJIS, r'\<span class="emoji" data-emoji="\g<0>"\>\</span\>', tweet["tweet_text"])

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


def get_tweets_status():
    totals_emotions = {}
    totals_groups = {}

    with DB_Handler() as handler:
        _tweets = handler.get_all_tagged()

        for _tweet in _tweets:
            emotions = get_emotions_list(_tweet)

            results = [(get_sentiment(emotions[i], emotions[j]), (emotions[i][0] + emotions[j][0]) / 2)
                       for i in range(len(emotions))
                       for j in range(i + 1, len(emotions))
                       if get_sentiment(emotions[i], emotions[j]) != "conflict"
                       if emotions[i][0] != 0 and emotions[j][0] != 0
                       ] + [("-", 0)] * 5

            results.sort(reverse=True, key=lambda x: x[1])

            groups = totalize_groups(results)

            emotions.sort(reverse=True)
            emotions = [emotion[1]
                        for emotion in emotions
                        if emotion[0] > 0
                        ][:2]

            for emotion in emotions:
                totals_emotions[emotion] = totals_emotions.get(emotion, 0) + 1

            groups = [(groups[group], group) for group in groups]
            groups.sort(reverse=True)

            for group in groups[:1]:
                totals_groups[group[1]] = totals_groups.get(group[1], 0) + 1

    return totals_emotions, totals_groups


def get_emotions_list(_tweet):
    emotions = [[_tweet.joy / _tweet.totals, "joy"],
                [_tweet.trust / _tweet.totals, "trust"],
                [_tweet.fear / _tweet.totals, "fear"],
                [_tweet.surprise / _tweet.totals, "surprise"],
                [_tweet.sadness / _tweet.totals, "sadness"],
                [_tweet.disgust / _tweet.totals, "disgust"],
                [_tweet.anger / _tweet.totals, "anger"],
                [_tweet.anticipation / _tweet.totals, "anticipation"],
                [_tweet.none / _tweet.totals, "none"],
                [_tweet.none / _tweet.totals, "none"]]

    emotions.sort(reverse=True)

    value = len(emotions)
    for i, emotion in enumerate(emotions):
        if emotion[0] == 0:
            value = 0

        must_reduce = i < len(emotions) - 1 and emotions[i][0] != emotions[i + 1][0]

        emotion[0] = value

        if must_reduce:
            value = len(emotions) - (i + 1)

        emotions[i] = tuple(emotion)

    return emotions


def tweet_add_sentiments(tweet):
    with DB_Handler() as handler:
        _tweet = handler.get_tagged(tweet['tweet_id'])

        emotions = get_emotions_list(_tweet)

    for emotion in emotions:
        tweet[emotion[1]] = emotion[0]

    return emotions


def get_sentiment(emotion_a, emotion_b):
    if not (emotion_a[1], emotion_b[1]) in DYADS:
        return DYADS.get((emotion_b[1], emotion_a[1]), "conflict")
    else:
        return DYADS.get((emotion_a[1], emotion_b[1]), "conflict")


if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port)
