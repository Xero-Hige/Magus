from gensim.models import KeyedVectors


class EmbeddingHandler:
    def __init__(self, model_name, embedding_size, matrix_height):
        self.features_vectors = KeyedVectors.load('/w2v_models/{}.mdl'.format(model_name))
        self.embedding_size = embedding_size
        self.matrix_height = matrix_height

    def get_embedding(self, feature):
        if feature in self.features_vectors:
            return [x for x in self.features_vectors[feature]]

        return [0] * self.embedding_size

    def get_embedding_matrix(self, feature_list):
        matrix = []

        for feature in feature_list:
            matrix.append(self.get_embedding(feature))

        while len(matrix) < self.matrix_height:
            matrix.append(self.get_embedding(""))

        while len(matrix) > self.matrix_height:
            matrix.pop()

        return
