import gensim

from libs.sentence_yield import TrainSentenceGenerator
from tokenizer.word_tokenizer import WordTokenizer


def generate_embeddings():
    sentences = TrainSentenceGenerator(["../tweets", "../bulk"], WordTokenizer)
    model = gensim.models.Word2Vec(sentences, min_count=1)

    a = model.most_similar(positive=['macri'], topn=2)
    print (a)


generate_embeddings()
