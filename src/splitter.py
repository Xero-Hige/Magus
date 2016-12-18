from __future__ import absolute_import, print_function, unicode_literals

from KafkaBroker import KafkaReader, KafkaWriter

class TweetSplitter():

    def process(self, tweet_dict):
        values = {}

        if not "user" in tweet_dict:
            return None

        values["at_user"] = tweet_dict["user"]["screen_name"]
        values["display_name"] = tweet_dict["user"]["name"].title()
        values["user_location"] = tweet_dict["user"]["location"]
        values["user_image"] = tweet_dict["user"]["profile_image_url"].replace("_normal.jpg", ".jpg")
        values["user_back"] = tweet_dict["user"].get("profile_banner_url", " ")
        values["text"] = tweet_dict["text"]

        try:
            if "coordinates" in tweet_dict and tweet_dict["coordinates"]:
                values["latitude"] = tweet_dict["coordinates"]["coordinates"][1]
                values["longitude"] = tweet_dict["coordinates"]["coordinates"][0]


            elif "geo" in tweet_dict and tweet_dict["geo"]:
                values["latitude"] = tweet_dict["geo"]["coordinates"][1]
                values["longitude"] = tweet_dict["geo"]["coordinates"][0]

            elif "place" in tweet_dict and tweet_dict["place"]:
                values["latitude"] = tweet_dict["place"]["bounding_box"]["coordinates"][0][0][1]
                values["latitude"] += tweet_dict["place"]["bounding_box"]["coordinates"][0][1][1]
                values["latitude"] += tweet_dict["place"]["bounding_box"]["coordinates"][0][2][1]
                values["latitude"] += tweet_dict["place"]["bounding_box"]["coordinates"][0][3][1]
                values["latitude"] /= 4

                values["longitude"] = tweet_dict["place"]["bounding_box"]["coordinates"][0][0][0]
                values["longitude"] += tweet_dict["place"]["bounding_box"]["coordinates"][0][1][0]
                values["longitude"] += tweet_dict["place"]["bounding_box"]["coordinates"][0][2][0]
                values["longitude"] += tweet_dict["place"]["bounding_box"]["coordinates"][0][3][0]
                values["longitude"] /= 4



        except Exception as e:
            values["latitude"] = "0"
            values["longitude"] = "0"

        if "place" in tweet_dict and tweet_dict["place"]:
            values["country"] = tweet_dict["place"]["country"]
        else:
            values["country"] = None

        return values

def main():
    tsp = TweetSplitter()
    reader = KafkaReader(b'tweetsInput')
    writer = KafkaWriter(b'parsedTweets')
    while True:
        tweet = reader.read()

        if not tweet:
            break

        dict = tsp.process(tweet)

        if dict:
            writer.write(dict)


if __name__ == '__main__':
    main()