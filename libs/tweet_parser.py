import json as Serializer


class TweetParser:

	@staticmethod
	def parse_from_json_file(filename):

		with open(filename,'r') as _file:
			return self.parse_from_json_string(_file.read())

	def parse_from_json_string(json_string):
		tweet = Serializer.loads(json_string)

		if not "user" in tweet:
            return None

		tweet_dict = {}

		tweet_dict["at_user"] = tweet_dict["user"]["screen_name"]
        tweet_dict["display_name"] = tweet_dict["user"]["name"].title()
        tweet_dict["user_location"] = tweet_dict["user"]["location"]
        tweet_dict["user_image"] = tweet_dict["user"]["profile_image_url"].replace("_normal.jpg", ".jpg")
        tweet_dict["user_back"] = tweet_dict["user"].get("profile_banner_url", " ")

		tweet_dict["text"] = tweet_dict["text"].encode("utf-8", 'replace').decode("utf-8")

		return tweet_dict 
