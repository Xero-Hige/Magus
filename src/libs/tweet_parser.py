import json as Serializer

class TweetParser:

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
			tweet_dict["text"] = tweet["extended_tweet"]["full_text"].encode("utf-8", 'replace').decode("utf-8")
		else:
			tweet_dict["text"] = tweet["text"].encode("utf-8", 'replace').decode("utf-8")

		return tweet_dict
