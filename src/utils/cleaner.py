import os
import sys
from subprocess import Popen, PIPE

import libs.tweet_parser as tweet_parser


def main():
    cleaning_dir = sys.argv[1]

    for tweet_file in os.listdir(cleaning_dir):
        tweet = tweet_parser.TweetParser.parse_from_json_file(os.path.join(cleaning_dir, tweet_file))

        correct_name = "{}.json".format(tweet["tweet_id"])

        if correct_name == tweet_file:
            continue

        print(tweet_file, "<--->", correct_name)

        p = Popen(["mv", tweet_file, correct_name], stdout=PIPE, stdin=PIPE, stderr=PIPE, cwd=cleaning_dir)
        p.communicate(input=b'\n')


main()
