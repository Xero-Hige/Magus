from libs.db_tweet import DB_Handler
from libs.tweet_anonymize import full_anonymize_tweet
from libs.tweet_parser import TweetParser


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
