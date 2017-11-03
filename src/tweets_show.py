import os
import random
import re
from subprocess import PIPE, Popen

from flask import Flask, redirect, render_template, request

from libs.db_tweet import DB_Handler, UNCLASIFIED, get_sentiment_emotions
from libs.sentiments_handling import ANGER, ANGRY, ANTICIPATION, DISGUST, DYADS, FEAR, HAPPY, JOY, NONE, SAD, SADNESS, \
    SURPRISE, TRUST
from libs.tweet_anonymize import full_anonymize_tweet
from libs.tweet_parser import TweetParser
from new_interface import new_interface
from utils.tweets_scrapper import do_scrapping

app = Flask(__name__)
app.register_blueprint(new_interface)

app.config['TEMPLATES_AUTO_RELOAD'] = True

EMOJIS = re.compile(u"\\ud83d", flags=re.UNICODE)


@app.route('/classify', methods=["GET"])
def classify_get():
    tweets = ["../tweets/{}".format(x) for x in os.listdir("../tweets")] \
             + ["../bulk/{}".format(x) for x in os.listdir("../bulk")]

    tweet = load_tweet(random.choice(tweets))

    return render_template("tweet_catalog.html", tweet=tweet, max=max)


@app.route('/classifyEsp', methods=["GET"])
def classify_esp_get():
    tweets = ["../tweets/{}".format(x) for x in os.listdir("../tweets")] \
             + ["../bulk/{}".format(x) for x in os.listdir("../bulk")]

    tweet = load_tweet(random.choice(tweets))

    return render_template("tweet_catalog_esp.html", tweet=tweet, max=max)


@app.route('/classify_old', methods=["GET"])
def classify_get_old():
    tweets = ["../tweets/{}".format(x) for x in os.listdir("../tweets")] \
             + ["../bulk/{}".format(x) for x in os.listdir("../bulk")]

    tweet = load_tweet(random.choice(tweets))

    return render_template("tweet_catalog_old.html", tweet=tweet, max=max)


@app.route('/classify_new', methods=["GET"])
def classify_get_new():
    tweets = ["../tweets/{}".format(x) for x in os.listdir("../tweets")] \
             + ["../bulk/{}".format(x) for x in os.listdir("../bulk")]

    tweet = load_tweet(random.choice(tweets))

    return render_template("catalog_alternative.html", tweet=tweet, max=max)


@app.route('/classify/<int:tweet_id>', methods=["GET"])
def classify_exact_get(tweet_id):
    tweet_id = "{}.json".format(tweet_id)
    demo_tweets = os.listdir("../tweets")
    bulk_tweets = os.listdir("../bulk")

    if str(tweet_id) in demo_tweets:
        tweet = load_tweet("../tweets/{}".format(tweet_id))
    elif str(tweet_id) in bulk_tweets:
        tweet = load_tweet("../bulk/{}".format(tweet_id))
    else:
        return redirect("/add")

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
        print("DEBUG - Script Error: ", stdout_data)

    p = Popen(["ruby", "uploader.rb", "tweets/{}.json".format(tweet_id), "../tweets/{}.json".format(tweet_id)],
              stdout=PIPE, stdin=PIPE, stderr=PIPE)

    stdout_data = p.communicate(input=b'\n')
    if "err" in str(stdout_data).lower():
        print("DEBUG - Script Error: ", stdout_data)

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

        p = Popen(["git", "config", "user.name", "{}".format(os.environ.get('GITHUB_USER', ""))],
                  stdout=PIPE, stdin=PIPE, stderr=PIPE, cwd='./upload')
        p.communicate(input=b'\n')
        p = Popen(["git", "config", "user.email", "{}".format(os.environ.get('GITHUB_EMAIL', ""))],
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

        p = Popen(["git", "add", "bulk/*"],
                  stdout=PIPE, stdin=PIPE, stderr=PIPE, cwd='./upload')
        stdout_data = p.communicate(input=b'\n')
        print("DEBUG - INFO : ", stdout_data)

        p = Popen(["git", "commit", "-m",
                   "New bulk added with Location={} :: Topics={} ".format(locations, topics)],
                  stdout=PIPE, stdin=PIPE, stderr=PIPE, cwd='./upload')
        stdout_data = p.communicate(input=b'\n')
        print("DEBUG - INFO : ", stdout_data)

        p = Popen(["git", "pull", "origin", "tweets"],
                  stdout=PIPE, stdin=PIPE, stderr=PIPE, cwd='./upload')
        stdout_data = p.communicate(input=b'\n')
        print("DEBUG - INFO : ", stdout_data)

        p = Popen(["git", "push", "--set-upstream", "origin", "tweets"],
                  stdout=PIPE, stdin=PIPE, stderr=PIPE, cwd='./upload')
        stdout_data = p.communicate(
                input=bytes('{}\n{}\n'.format(
                        os.environ.get('GITHUB_USER', ""),
                        os.environ.get('GITHUB_PASS', "")),
                        'utf-8'))

        print("DEBUG - INFO : ", stdout_data)

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
            tweet.joy += 1 if dyad_a == JOY else 0
            tweet.sadness += 1 if dyad_a == SADNESS else 0
            tweet.trust += 1 if dyad_b == TRUST else 0
            tweet.disgust += 1 if dyad_b == DISGUST else 0
            tweet.fear += 1 if dyad_c == FEAR else 0
            tweet.anger += 1 if dyad_c == ANGER else 0
            tweet.surprise += 1 if dyad_d == SURPRISE else 0
            tweet.anticipation += 1 if dyad_d == ANTICIPATION else 0

        if sentiment == NONE:
            tweet.none += 1
        else:
            emotions = get_sentiment_emotions(sentiment)

            tweet.joy += 2 if JOY in emotions else 0
            tweet.sadness += 2 if SADNESS in emotions else 0
            tweet.trust += 2 if TRUST in emotions else 0
            tweet.disgust += 2 if DISGUST in emotions else 0
            tweet.fear += 2 if FEAR in emotions else 0
            tweet.anger += 2 if ANGER in emotions else 0
            tweet.surprise += 2 if SURPRISE in emotions else 0
            tweet.anticipation += 2 if ANTICIPATION in emotions else 0

        tweet.ironic += 3 if is_ironic else 0

        tweet.totals += 3 if tweet.totals != 1 else 2
        # TODO: LOCK RELEASE


@app.route('/classify', methods=["POST"])
def classify_post():
    action = request.form["action"]

    if action == 'skip':
        return redirect("/classify")

    classify_tweet()

    return redirect("/classify")


@app.route('/classifyEsp', methods=["POST"])
def classify_esp_post():
    action = request.form["action"]

    if action == 'skip':
        return redirect("/classifyEsp")

    classify_tweet()

    return redirect("/classifyEsp")


@app.route('/status', methods=["GET"])
def status():
    totals_emotions, totals_groups, samples = get_tweets_status()
    return render_template("DB_status.html", emotions=totals_emotions, groups=totals_groups, samples=samples)


def load_tweet(tweet_file_name):
    tweet = TweetParser.parse_from_json_file(tweet_file_name)

    tweet["tweet_text"] = full_anonymize_tweet(tweet.get(TweetParser.TWEET_TEXT, ""))

    with DB_Handler() as handler:
        _tweet = handler.get_tagged(tweet["tweet_id"])

        groups = _tweet.get_groups_percent()
        sentiments = _tweet.get_sentiment_list()
        emotions = _tweet.get_emotions_list()

    tweet_dict_add_emotions(tweet, emotions)

    tweet["sentiments"] = sentiments
    tweet["groups"] = groups

    return tweet


def get_tweets_status():
    totals_emotions = {}
    totals_groups = {}

    demo_tweets = os.listdir("../tweets")
    bulk_tweets = os.listdir("../bulk")

    samples = {HAPPY: [], SAD: [], ANGRY: [], NONE: [], UNCLASIFIED: []}

    with DB_Handler() as handler:
        _tweets = handler.get_all_tagged()

        for _tweet in _tweets:

            tweet_filename = "{}.json".format(_tweet.id)

            if _tweet.totals < 3:
                continue

            if tweet_filename not in demo_tweets and tweet_filename not in bulk_tweets:
                continue

            emotions = _tweet.get_emotions_list()
            emotions = [emotion[1]
                        for emotion in emotions
                        if emotion[0] > 0
                        ][:2]

            for emotion in emotions:
                totals_emotions[emotion] = totals_emotions.get(emotion, 0) + 1

            group = _tweet.get_tweet_group()
            totals_groups[group] = totals_groups.get(group, 0) + 1

            samples[group].append((_tweet.id, _tweet.get_tweet_sentiment()))

            samples_collected = len(samples[group])
            if samples_collected > 10:
                samples[group].pop(random.choice([0, samples_collected - 1]))

    return totals_emotions, totals_groups, samples


def tweet_dict_add_emotions(tweet, emotions):
    for emotion in emotions:
        tweet[emotion[1]] = emotion[0]


def get_sentiment(emotion_a, emotion_b):
    if not (emotion_a[1], emotion_b[1]) in DYADS:
        return DYADS.get((emotion_b[1], emotion_a[1]), "conflict")
    else:
        return DYADS.get((emotion_a[1], emotion_b[1]), "conflict")


if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port)
