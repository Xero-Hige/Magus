from gensim.models import KeyedVectors


class EmbeddingMapper:
    def __init__(self, vectors_file, map_size, embedding_size):
        self.map_size = map_size
        self.embedding_size = embedding_size
        self.embedding_lookup = KeyedVectors.load(vectors_file)

    def __get_feature_vector(self, token):
        if token in self.embedding_lookup:
            return [[x] for x in self.embedding_lookup[token]]

        return [[0]] * self.embedding_size

    def map_features(self, features_list, tweet_id):

        tweet_vectors = []

        for feature in features_list:
            tweet_vectors.append(self.__get_feature_vector(feature))

        while len(tweet_vectors) < self.map_size:
            tweet_vectors.append([[0]] * self.embedding_size)

        if len(tweet_vectors) > self.map_size:
            print("Exceed map size: {}. Expected {}, Got {}".format(tweet_id, self.map_size, len(tweet_vectors)))
            tweet_vectors = tweet_vectors[:self.map_size]

        return tweet_vectors
