import json as Serializer


class TweetParser:
    TWEET_TEXT = "tweet_text"
    TWEET_ID = "tweet_id"
    USER_BACK = "user_back"
    USER_IMAGE = "user_image"
    USER_LOCATION = "user_location"
    DISPLAY_NAME = "display_name"
    AT_USER = "at_user"
    LONGITUDE = "longitude"
    LATITUDE = "latitude"
    ORIGINAL_TEXT = "original"

    @staticmethod
    def parse_from_json_file(filename):
        with open(filename, 'r') as _file:
            return TweetParser.parse_from_json_string(_file.read())

    @staticmethod
    def parse_from_json_string(json_string):
        tweet = Serializer.loads(json_string)
        return TweetParser.parse_from_dict(tweet)

    @staticmethod
    def parse_from_dict(tweet):
        if "user" not in tweet:
            return None

        tweet_dict = {}

        tweet_dict[TweetParser.AT_USER] = tweet["user"]["screen_name"]
        tweet_dict[TweetParser.DISPLAY_NAME] = tweet["user"]["name"].title()
        tweet_dict[TweetParser.USER_LOCATION] = tweet["user"]["location"]
        tweet_dict[TweetParser.USER_IMAGE] = tweet["user"]["profile_image_url"].replace("_normal.jpg", ".jpg")
        tweet_dict[TweetParser.USER_BACK] = tweet["user"].get("profile_banner_url", " ")

        tweet_dict["publish_date"] = tweet["created_at"].split()[1:4]

        if "truncated" in tweet and "extended_tweet" in tweet:
            tweet_dict[TweetParser.TWEET_TEXT] = tweet["extended_tweet"]["full_text"].encode("utf-8", 'replace').decode(
                    "utf-8")
        elif "retweeted_status" in tweet and "extended_tweet" in tweet["retweeted_status"]:
            tweet_dict[TweetParser.TWEET_TEXT] = tweet["retweeted_status"]["extended_tweet"]["full_text"].encode(
                    "utf-8", 'replace').decode(
                    "utf-8")
        elif "retweeted_status" in tweet and "text" in tweet["retweeted_status"]:
            tweet_dict[TweetParser.TWEET_TEXT] = tweet["retweeted_status"]["text"].encode("utf-8", 'replace').decode(
                    "utf-8")
        else:
            tweet_dict[TweetParser.TWEET_TEXT] = tweet["text"].encode("utf-8", 'replace').decode("utf-8")

        tweet_dict[TweetParser.ORIGINAL_TEXT] = tweet_dict[TweetParser.TWEET_TEXT]

        try:
            if "coordinates" in tweet and tweet["coordinates"]:
                tweet_dict[TweetParser.LATITUDE] = tweet["coordinates"]["coordinates"][1]
                tweet_dict[TweetParser.LONGITUDE] = tweet["coordinates"]["coordinates"][0]

            elif "geo" in tweet and tweet["geo"]:
                tweet_dict[TweetParser.LATITUDE] = tweet["geo"]["coordinates"][1]
                tweet_dict[TweetParser.LONGITUDE] = tweet["geo"]["coordinates"][0]

            elif "place" in tweet and tweet["place"]:
                tweet_dict[TweetParser.LATITUDE] = tweet["place"]["bounding_box"]["coordinates"][0][0][1]
                tweet_dict[TweetParser.LATITUDE] += tweet["place"]["bounding_box"]["coordinates"][0][1][1]
                tweet_dict[TweetParser.LATITUDE] += tweet["place"]["bounding_box"]["coordinates"][0][2][1]
                tweet_dict[TweetParser.LATITUDE] += tweet["place"]["bounding_box"]["coordinates"][0][3][1]
                tweet_dict[TweetParser.LATITUDE] /= 4

                tweet_dict[TweetParser.LONGITUDE] = tweet["place"]["bounding_box"]["coordinates"][0][0][0]
                tweet_dict[TweetParser.LONGITUDE] += tweet["place"]["bounding_box"]["coordinates"][0][1][0]
                tweet_dict[TweetParser.LONGITUDE] += tweet["place"]["bounding_box"]["coordinates"][0][2][0]
                tweet_dict[TweetParser.LONGITUDE] += tweet["place"]["bounding_box"]["coordinates"][0][3][0]
                tweet_dict[TweetParser.LONGITUDE] /= 4
            else:
                tweet_dict[TweetParser.LATITUDE] = 0
                tweet_dict[TweetParser.LONGITUDE] = 0

        except Exception as e:
            tweet_dict[TweetParser.LATITUDE] = 0
            tweet_dict[TweetParser.LONGITUDE] = 0

        if "place" in tweet and tweet["place"]:
            tweet_dict["country"] = tweet["place"]["country"]
        else:
            tweet_dict["country"] = None

        tweet_dict[TweetParser.TWEET_ID] = tweet["id_str"]

        if "retweeted_status" in tweet:
            tweet_dict[TweetParser.TWEET_ID] = tweet["retweeted_status"]["id_str"]

        tweet_dict["tweet_lang"] = tweet.get("lang", "")

        if tweet.get("place"):
            tweet_dict["tweet_place"] = tweet.get("place", {}).get("name", "")
        else:
            tweet_dict["tweet_place"] = ""

        tweet_dict["tweet_user_lang"] = tweet.get("user", {}).get("lang", "")

        tweet_dict["tweet_hashtags"] = []

        for hashtag in tweet.get("entities", {}).get("hashtags", []):
            tweet_dict["tweet_hashtags"].append(hashtag.get("text", ""))

        tweet_dict["tweet_mentions"] = 0

        for _ in tweet.get("entities", {}).get("user_mentions", []):
            tweet_dict["tweet_mentions"] += 1

        tweet_dict["tweet_media"] = {}

        try:
            if tweet.get("extended_entities"):
                media = tweet.get("extended_entities", {}).get("media", [])
                for m in media:
                    tweet_dict["tweet_media"][m["type"]] = tweet["tweet_media"].get(m["type"], 0) + 1
        except:
            pass

        return tweet_dict
