import json as Serializer

class TweetParser:

	TWEET_TEXT = "tweet_text"

	@staticmethod
	def parse_from_json_file(filename):
		with open(filename,'r') as _file:
			return TweetParser.parse_from_json_string(_file.read())

	@staticmethod
	def parse_from_json_string(json_string):
		tweet = Serializer.loads(json_string)

		if not "user" in tweet:
			return None

		tweet_dict = {}

		tweet_dict["at_user"] = tweet["user"]["screen_name"]
		tweet_dict["display_name"] = tweet["user"]["name"].title()
		tweet_dict["user_location"] = tweet["user"]["location"]
		tweet_dict["user_image"] = tweet["user"]["profile_image_url"].replace("_normal.jpg", ".jpg")
		tweet_dict["user_back"] = tweet["user"].get("profile_banner_url", " ")

		if "truncated" in tweet and "extended_tweet" in tweet:
			tweet_dict[TweetParser.TWEET_TEXT] = tweet["extended_tweet"]["full_text"].encode("utf-8", 'replace').decode("utf-8")
		else:
			tweet_dict[TweetParser.TWEET_TEXT] = tweet["text"].encode("utf-8", 'replace').decode("utf-8")

		try:
			if "coordinates" in tweet and tweet["coordinates"]:
				tweet_dict["latitude"] = tweet["coordinates"]["coordinates"][1]
				tweet_dict["longitude"] = tweet["coordinates"]["coordinates"][0]

			elif "geo" in tweet and tweet["geo"]:
				tweet_dict["latitude"] = tweet["geo"]["coordinates"][1]
				tweet_dict["longitude"] = tweet["geo"]["coordinates"][0]

			elif "place" in tweet and tweet["place"]:
				tweet_dict["latitude"] = tweet["place"]["bounding_box"]["coordinates"][0][0][1]
				tweet_dict["latitude"] += tweet["place"]["bounding_box"]["coordinates"][0][1][1]
				tweet_dict["latitude"] += tweet["place"]["bounding_box"]["coordinates"][0][2][1]
				tweet_dict["latitude"] += tweet["place"]["bounding_box"]["coordinates"][0][3][1]
				tweet_dict["latitude"] /= 4

				tweet_dict["longitude"] = tweet["place"]["bounding_box"]["coordinates"][0][0][0]
				tweet_dict["longitude"] += tweet["place"]["bounding_box"]["coordinates"][0][1][0]
				tweet_dict["longitude"] += tweet["place"]["bounding_box"]["coordinates"][0][2][0]
				tweet_dict["longitude"] += tweet["place"]["bounding_box"]["coordinates"][0][3][0]
				tweet_dict["longitude"] /= 4

		except Exception as e:
			tweet_dict["latitude"] = "0"
			tweet_dict["longitude"] = "0"

		if "place" in tweet and tweet["place"]:
			tweet_dict["country"] = tweet["place"]["country"]
		else:
			tweet_dict["country"] = None

		tweet["tweet_id"] = tweet["id_str"]

		tweet["tweet_lang"] = tweet.get("lang", "")

		if tweet.get("place"):
			tweet["tweet_place"] = tweet.get("place", {}).get("name", "")
		else:
			tweet["tweet_place"] = ""

		tweet["tweet_user_lang"] = tweet.get("user", {}).get("lang", "")

		tweet["tweet_hashtags"] = []
		for hashtag in tweet.get("entities", {}).get("hashtags", []):
			tweet["tweet_hashtags"].append(hashtag.get("text", ""))

		tweet["tweet_mentions"] = 0
		for _ in tweet.get("entities", {}).get("user_mentions", []):
			tweet["tweet_mentions"] += 1

		tweet["tweet_media"] = {}
		if tweet.get("extended_entities"):
			media = tweet.get("extended_entities", {}).get("media", [])
			for m in media:
				tweet["tweet_media"][m["type"]] = tweet["tweet_media"].get(m["type"], 0) + 1


		return tweet_dict
