import os
import random

from flask import Blueprint, redirect, render_template, request

from libs.db_tweet import DB_Handler
from tweets_show import load_tweet

APP_ROUTE = '/en'

new_interface = Blueprint('new_interface', __name__,
                          template_folder='templates')


@new_interface.route(APP_ROUTE + '/classify', methods=["GET"])
def classify_get():
    tweets = ["../tweets/{}".format(x) for x in os.listdir("../tweets")] \
             + ["../bulk/{}".format(x) for x in os.listdir("../bulk")]

    tweet = load_tweet(random.choice(tweets))

    return render_template("catalog_alternative.html", tweet=tweet, max=max, app_route=APP_ROUTE)


@new_interface.route(APP_ROUTE + '/add_classification/<int:id>', methods=["GET"])
def classify_tweet(tweet_id):
    tweet_class = request.args.get('class')

    classify_tweet_db(tweet_id, tweet_class)

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
