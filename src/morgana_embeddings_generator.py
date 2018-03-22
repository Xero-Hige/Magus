import gensim

from libs.sentence_yield import TrainSentenceGenerator
from morgana_config_handler import EMBEDDINGS_FILES, EMBEDDING_SIZES, TWEETS_DIRS
from tokenizer.char_tokenizer import CharTokenizer
from tokenizer.raw_char_tokenizer import RawCharTokenizer
from tokenizer.word_tokenizer import WordTokenizer


def generate_word_embeddings():
    print("Generating embeddings for words")
    sentences = TrainSentenceGenerator(["../{}".format(x) for x in TWEETS_DIRS], WordTokenizer)
    model = gensim.models.Word2Vec(sentences, min_count=3, size=EMBEDDING_SIZES["words"])
    word_vector = model.wv
    word_vector.save('./{}.mdl'.format(EMBEDDINGS_FILES["words"]))


def generate_raw_chars_embeddings():
    print("Generating embeddings for raw_chars")
    sentences = TrainSentenceGenerator(["../{}".format(x) for x in TWEETS_DIRS], RawCharTokenizer)
    model = gensim.models.Word2Vec(sentences, min_count=5, size=EMBEDDING_SIZES["raw_chars"])
    word_vector = model.wv
    word_vector.save('./{}.mdl'.format(EMBEDDINGS_FILES["raw_chars"]))


def generate_chars_embeddings():
    print("Generating embeddings for chars")
    sentences = TrainSentenceGenerator(["../{}".format(x) for x in TWEETS_DIRS], CharTokenizer)
    model = gensim.models.Word2Vec(sentences, min_count=5, size=EMBEDDING_SIZES["chars"])
    word_vector = model.wv
    word_vector.save('./{}.mdl'.format(EMBEDDINGS_FILES["chars"]))


def main():
    print("Generating embeddings files")
    generate_word_embeddings()
    generate_raw_chars_embeddings()
    generate_chars_embeddings()
    print("Generating embeddings for words")


if __name__ == '__main__':
    main()
