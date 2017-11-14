import json

from libs.lexicon import Lexicon
from libs.tweet_anonymize import full_anonymize_tweet
from libs.tweet_fetcher import TweetsFetcher
from libs.tweet_parser import TweetParser

lexicon = Lexicon("lexicons/es_lexicon.lx", "es")
downloaded = 0

for tweet in TweetsFetcher(langs=["es"]):

    parsed_tweet = TweetParser.parse_from_dict(tweet)
    if not parsed_tweet:
        continue

    if "es" not in parsed_tweet["tweet_lang"].lower():
        continue

    text = full_anonymize_tweet(parsed_tweet[TweetParser.TWEET_TEXT].lower())

    tag, value = lexicon.auto_tag_sentence(text)

    if (value > 3 and tag != "neutral") or (value > 10 and tag == "neutral"):
        with open("tweets_bashfull/{}/{}.json".format(tag, parsed_tweet[TweetParser.TWEET_ID]), 'w') as output:
            output.write(json.dumps(tweet))
            downloaded += 1
            print("Total downloaded:{}  <<{}>>".format(downloaded, tag))
