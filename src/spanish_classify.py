import os
import random

from flask import Blueprint, redirect, render_template, request

from classify_functions import classify_tweet_db, load_tweet
from libs.db_tweet import UNCLASIFIED
from libs.lexicon import Lexicon

APP_ROUTE = '/es'

spanish_classify = Blueprint('spanish_classify', __name__,
                             template_folder='templates')

LEXICONS = [Lexicon("./lexicons/en_lexicon.lx", lang="en"),
            Lexicon("./lexicons/es_lexicon.lx", lang="es"),
            Lexicon("./lexicons/pt_lexicon.lx", lang="pt")]


@spanish_classify.route(APP_ROUTE + '/classify', methods=["GET"])
def classify_get():
    tweets = ["../tweets/{}".format(x) for x in os.listdir("../tweets")] \
             + ["../bulk/{}".format(x) for x in os.listdir("../bulk")]

    tweet = load_tweet(random.choice(tweets))

    return render_template("catalog_alternative.html", tweet=tweet, max=max, app_route=APP_ROUTE, lang='es')


@spanish_classify.route(APP_ROUTE + '/validate', methods=["GET"])
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


@spanish_classify.route(APP_ROUTE + '/validate', methods=["POST"])
def validate_tag_post():
    validation = request.form["validation"]

    if validation == "skip":
        return redirect(APP_ROUTE + "/validate")

    modify_value = 2 if validation == "yes" else -3

    emotion = request.form["classification"]
    tweet_id = request.form["tweet_id"]

    classify_tweet_db(str(tweet_id), emotion, modify_value)

    return redirect(APP_ROUTE + "/validate")


@spanish_classify.route(APP_ROUTE + '/add_classification/<string:tweet_id>', methods=["GET"])
def classify_tweet(tweet_id):
    tweet_class = request.args.get('class')

    classify_tweet_db(tweet_id, tweet_class)

    return redirect(APP_ROUTE + '/classify')
