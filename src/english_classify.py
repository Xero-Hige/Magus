import os
import random

from flask import Blueprint, redirect, render_template, request

from classify_functions import classify_tweet_db, load_tweet
from lexicons.lexicons import LEXICONS
from libs.db_tweet import UNCLASIFIED

APP_ROUTE = '/en'

english_classify = Blueprint('english_classify', __name__,
                             template_folder='templates')


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
        classification = UNCLASIFIED
        auto = "UNCLASS"
        for lexicon in LEXICONS:
            if lexicon.get_associated_lang() in tweet["tweet_user_lang"].lower():
                classification, level = lexicon.auto_tag_sentence(tweet["tweet_text"])
                auto = "LEXICON {} with level ({})".format(lexicon.get_associated_lang(), level)
                break

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


@english_classify.route(APP_ROUTE + '/add_classification/<string:tweet_id>', methods=["GET"])
def classify_tweet(tweet_id):
    tweet_class = request.args.get('class')

    classify_tweet_db(tweet_id, tweet_class)

    return redirect(APP_ROUTE + '/classify')
