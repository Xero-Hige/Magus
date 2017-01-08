import json
import os


def main():
    for tweet_file_name in os.listdir("tweets"):
        with open("../tweets/" + tweet_file_name) as tweet_file:
            tweet_dump = tweet_file.read()

        tweet = json.loads(tweet_dump, encoding="utf-8")

        if not tweet:
            continue

        tweet_text = tweet.get("text", "")
        tweet_lang = tweet.get("lang", "")
        if (tweet.get("place")):
            tweet_place = tweet.get("place", {}).get("name", "")
        else:
            tweet_place = ""
        tweet_user_lang = tweet.get("user", {}).get("lang", "")
        tweet_hashtags = []
        for hashtag in tweet.get("entities", {}).get("hashtags", []):
            tweet_hashtags.append(hashtag.get("text", ""))
        tweet_mentions = 0
        for x in tweet.get("entities", {}).get("user_mentions", []):
            tweet_mentions += 1

        tweet_media = {}
        if (tweet.get("extended_entities")):
            media = tweet.get("extended_entities", {}).get("media", [])
            types = {}
            for m in media:
                types[m["type"]] = types.get(m["type"], 0) + 1

        print ("*" * 80)
        print ("\t--> Text: " + tweet_text + "\n")
        print ("\t--> Lang: " + tweet_lang + "\n")
        print ("\t--> User Lang: " + tweet_user_lang + "\n")
        print ("\t--> Place: " + tweet_place + "\n")
        print ("\t--> Mentions: " + str(tweet_mentions) + "\n")
        print ("\t--> Hashtags: ")
        for hashtag in tweet_hashtags:
            print ("\t\t*" + hashtag)
        print ("\t--> Media: ")
        for media in tweet_media:
            print ("\t\t* (" + media + "," + tweet_media[media] + ")")


main()
