import libs.tweet_parser as tweet_parser
from subprocess import Popen, PIPE

import sys
import os

def main()
    cleaning_dir = sys.argv[0]

    for tweet_file in os.listdir(cleaning_dir):
        tweet = parse_from_json_file(os.path.join(cleaning_dir,tweet_file))

        correct_name = "{}.json".format(tweet["id"])

        print(tweet_file,"<--->",correct_name)

        if correct_name == tweet_file:
            continue

        p = Popen(["mv", tweet_file , correct_name], stdout=PIPE, stdin=PIPE, stderr=PIPE)
        p.communicate(input=b'\n')
