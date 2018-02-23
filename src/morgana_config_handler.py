import json
import sys

try:
    with open("morgana_config.json") as f:
        config = json.loads(f.read())
except IOError:
    print("Error opening config file", file=sys.stderr)
    exit(-12)

MORGANA_CONFIGS = config
ENABLED_EMOTIONS = config["enabled_emotions"]
TWEETS_DIRS = config["tweets_dirs"]
EMBEDDING_SIZES = config["embeddings_sizes"]
MAX_FEATURES = config["max_features"]
EMBEDDINGS_FILES = config["embeddings_files"]
FILTER_SIZES = config["filter_sizes"]
NUMBER_OF_FILTERS = config["number_of_filters"]
HIDDEN_LAYERS_SIZE = config["streams_hidden_layers"]
