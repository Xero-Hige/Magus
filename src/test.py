from libs.tweet_parser import TweetParser

# import utils
# import utils.tweets_scrapper

for k, v in TweetParser.parse_from_json_file("something.json").items():
    print(k, v)
