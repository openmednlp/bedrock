import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from gensim.models import Phrases, Word2Vec
from bedrock import common
from sklearn.feature_extraction.text import CountVectorizer

def train_tfidf_vectorizer(X, persist_path=None):
    tfidf_vectorizer = TfidfVectorizer()
    tfidf_vectorizer.fit(X)

    common.save_pickle(tfidf_vectorizer, persist_path)

    return tfidf_vectorizer


def train_count_vectorizer(tokenized_sentences):
    cv = CountVectorizer()
    cv.fit(tokenized_sentences)

    global _count_vectorizer
    _count_vectorizer = cv

    return cv


def count_vectorizer_transform(sentence):
    return _count_vectorizer.transform(sentence).indices


def get_sentence_count_vector(sentence):
    return _count_vectorizer.transform(sentence).indices

def train_word2vec_vectorizer(tokenized_sentences,
                              group_by_phrases=False,
                              persist_path=None):
    # tokenized_sentences :
    #   input format is a list of sentences representet as list of tokens
    #   e.g. [
    #           [['sentence'],['one']],
    #           [['sentence'],['two']]
    #        ]

    # TODO: this could be also streamed directly from disk
    # TODO: if not tokenized
    # Try detecting phrases, not very good for our purpose atm
    if group_by_phrases:
        bigram_transformer = Phrases(tokenized_sentences)
        tokenized_sentences = bigram_transformer[tokenized_sentences]

    model = Word2Vec(tokenized_sentences, window=5, size=200)
    print('Learned vocab len: ', len(model.wv.vocab))

    common.save_pickle(model, persist_path)

    return model


def load_pickle(pickle_path):
    return pickle.load(pickle_path)