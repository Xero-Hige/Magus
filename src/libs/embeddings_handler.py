from gensim.models import KeyedVectors


class EmbeddingHandler:
    def __init__(self, model_name):
        self.word_vectors = KeyedVectors.load('w2v_models/{}.mdl'.format(model_name))

    def get_embedding(self, word, embedding_size):
        if word in self.word_vectors:
            return [x for x in self.word_vectors[word]]

        return [0] * embedding_size