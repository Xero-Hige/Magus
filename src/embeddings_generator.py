import gensim

from libs.sentence_yield import TrainSentenceGenerator
from tokenizer.char_tokenizer import CharTokenizer
from tokenizer.raw_char_tokenizer import RawCharTokenizer
from tokenizer.word_tokenizer import WordTokenizer


def generate_word_embeddings():
    sentences = TrainSentenceGenerator(["../tweets", "../bulk"], WordTokenizer)
    model = gensim.models.Word2Vec(sentences, min_count=3, size=300)
    word_vector = model.wv
    word_vector.save('./wordsEmbeddings.mdl')


def generate_raw_chars_embeddings():
    sentences = TrainSentenceGenerator(["../tweets", "../bulk"], RawCharTokenizer)
    model = gensim.models.Word2Vec(sentences, min_count=5, size=300)
    word_vector = model.wv
    word_vector.save('./rCharsEmbeddings.mdl')


def generate_chars_embeddings():
    sentences = TrainSentenceGenerator(["../tweets", "../bulk"], CharTokenizer)
    model = gensim.models.Word2Vec(sentences, min_count=5, size=300)
    word_vector = model.wv
    word_vector.save('./charsEmbeddings.mdl')


generate_word_embeddings()
generate_raw_chars_embeddings()
generate_chars_embeddings()
