import os
import random

from libs.lexicon import Lexicon

lexicon = Lexicon("lexicons/es_lexicon.lx","es")

for folder,_,files in os.walk("."):
    random.shuffle(files)

    emotion = folder.split("/")[-1]
    print("Validate --> {}".format(emotion))

    batch = 1

    for _file in files[:2]:
            tweet_id = _file.split(".")[0]
            output_dir = os.path.join(".","results","batch{}".format(batch))

            key_pressed = "y"

            if key_pressed == "y":
                output_dir = os.path.join(output_dir,"good")
                try:
                    os.makedirs(output_dir)
                except:
                    pass

                print(output_dir+"{}.json".format(tweet_id))

            elif key_pressed == "n":
                output_dir = os.path.join(output_dir,"bad")
                try:
                    os.makedirs(output_dir)
                except:
                    pass
                print(output_dir+"{}.json".format(tweet_id))

            else:
                print("BOBO")

            print("<<{}>> {}".format(emotion,tweet_id))
