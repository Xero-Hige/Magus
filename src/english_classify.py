import os
import random

from flask import Blueprint, redirect, render_template, request

from libs.db_tweet import DB_Handler, UNCLASIFIED
from libs.lexicon import Lexicon
from libs.tweet_anonymize import full_anonymize_tweet
from libs.tweet_parser import TweetParser

APP_ROUTE = '/en'

english_classify = Blueprint('english_classify', __name__,
                             template_folder='templates')

LEXICONS = [Lexicon("./lexicons/en_lexicon.lxc", lang="en")]


@english_classify.route(APP_ROUTE + '/classify', methods=["GET"])
def classify_get():
    tweets = ["../tweets/{}".format(x) for x in os.listdir("../tweets")] \
             + ["../bulk/{}".format(x) for x in os.listdir("../bulk")]

    tweet = load_tweet(random.choice(tweets))

    return render_template("catalog_alternative.html", tweet=tweet, max=max, app_route=APP_ROUTE, lang='en')


@english_classify.route(APP_ROUTE + '/validate', methods=["GET"])
def validate_tag_get():
    tweets = ["../tweets/{}".format(x) for x in os.listdir("../tweets")] \
             + ["../bulk/{}".format(x) for x in os.listdir("../bulk")]

    tweet = load_tweet(random.choice(tweets))

    if tweet["totals"] > 1:
        classification = tweet["tweet_emotion"]
        auto = "BD"
    else:
        classification = LEXICONS[0].auto_tag_sentence(tweet["tweet_text"]) if LEXICONS[0].get_associated_lang() in \
                                                                               tweet[
                                                                                   "tweet_user_lang"].lower() else UNCLASIFIED
        auto = "LEXICON " + LEXICONS[0].get_associated_lang()

    return render_template("tag_validator.html", tweet=tweet, max=max, app_route=APP_ROUTE,
                           classification=classification, auto=auto)


@english_classify.route(APP_ROUTE + '/validate', methods=["POST"])
def validate_tag_post():
    validation = request.form["validation"]

    if validation == "skip":
        return redirect(APP_ROUTE + "/validate")

    modify_value = 2 if validation == "yes" else -3

    emotion = request.form["classification"]
    tweet_id = request.form["tweet_id"]

    classify_tweet_db(str(tweet_id), emotion, modify_value)

    return redirect(APP_ROUTE + "/validate")


@english_classify.route(APP_ROUTE + '/add_classification/<int:tweet_id>', methods=["GET"])
def classify_tweet(tweet_id):
    tweet_class = request.args.get('class')

    classify_tweet_db(str(tweet_id), tweet_class)

    return redirect(APP_ROUTE + '/classify')


def classify_tweet_db(tweet_id, tweet_class, add_value=3):
    with DB_Handler() as handler:
        # TODO: LOCK TAKE
        tweet = handler.get_tagged(tweet_id)

        if tweet_class == "joy" or tweet_class == "love" or tweet_class == "optimism":
            tweet.joy = tweet.joy + add_value
        if tweet_class == "trust" or tweet_class == "love" or tweet_class == "submission":
            tweet.trust = tweet.trust + add_value
        if tweet_class == "fear" or tweet_class == "awe" or tweet_class == "submission":
            tweet.fear = tweet.fear + add_value
        if tweet_class == "surprise" or tweet_class == "awe" or tweet_class == "disapproval":
            tweet.surprise = tweet.surprise + add_value
        if tweet_class == "sadness" or tweet_class == "remorse" or tweet_class == "disapproval":
            tweet.sadness = tweet.sadness + add_value
        if tweet_class == "disgust" or tweet_class == "remorse" or tweet_class == "contempt":
            tweet.disgust = tweet.disgust + add_value
        if tweet_class == "anger" or tweet_class == "aggressiveness" or tweet_class == "contempt":
            tweet.anger = tweet.anger + add_value
        if tweet_class == "anticipation" or tweet_class == "aggressiveness" or tweet_class == "optimism":
            tweet.anticipation = tweet.anticipation + add_value

        tweet.totals += abs(add_value) if tweet.totals != 1 else abs(add_value) - 1
        # TODO: LOCK RELEASE


def load_tweet(tweet_file_name):
    tweet = TweetParser.parse_from_json_file(tweet_file_name)

    tweet["tweet_text"] = full_anonymize_tweet(tweet.get(TweetParser.TWEET_TEXT, ""))

    with DB_Handler() as handler:
        _tweet = handler.get_tagged(tweet["tweet_id"])

        emotions = _tweet.get_emotions_list()
        totals = _tweet.totals
        emotion = _tweet.get_tweet_emotion()

    tweet_dict_add_emotions(tweet, emotions)
    tweet["totals"] = totals
    tweet["tweet_emotion"] = emotion

    return tweet


def tweet_dict_add_emotions(tweet, emotions):
    for emotion in emotions:
        tweet[emotion[1]] = emotion[0]
