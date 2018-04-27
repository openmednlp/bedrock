from bedrock.processors.Processor import Processor
import spacy
from nltk import SnowballStemmer
from spacy.lang.de.stop_words import STOP_WORDS
import string

class SpacyProcessor(Processor):
    def __init__(self, lang='de'):
        self._nlp = spacy.load(lang)

        self.stemmer = SnowballStemmer(self._lang_convert[lang])

    def lemmatize(self, text_input):
        # Lematize string or list of texts.
        # Always returns list of texts.
        texts = self._to_list(text_input)
        lemmatized_texts = []
        for text in texts:
            doc = self._nlp(text)
            lemmatized_texts.append(
                ' '.join([token.lemma_ for token in doc])
            )
        return lemmatized_texts

    def sentence_tokenize(self, text_input):
        texts = self._to_list(text_input)
        sentence_tokenized_texts = []
        for text in texts:
            doc = self._nlp(text)
            sentence_tokenized_texts.append(
                [sent.string for sent in doc.sents]
            )
        return sentence_tokenized_texts

    def stem(self, text_input):
        print('Warning: No stemming in Spacy, using NLTK.')
        texts = self._to_list(text_input)
        stemmed_texts = []

        for text_tokens in self.tokenize(texts):

            stemmed_texts.append(
                ' '.join(
                    [self.stemmer.stem(token) for token in text_tokens]
                )
            )
        return stemmed_texts

    def tokenize(self, text_input):
        # Always returns list of token's list
        texts = self._to_list(text_input)
        tokenized_texts = []
        for text in texts:
            doc = self._nlp(text)
            tokenized_texts.append([token.text for token in doc])
        return tokenized_texts

    def remove_short(self, text_input, min_word_len):
        # TODO: tests and check
        # Remove short words.
        texts = self._to_list(text_input)
        if not min_word_len:
            return texts

        processed_text = []
        tokenized_texts = self.tokenize(texts)
        for text_tokens in tokenized_texts:
            processed_text.append(
                ' '.join(
                    [token for token in text_tokens if len(token) >= min_word_len]
                )
            )

        return processed_text

    def remove_stop_words(self, text_input):
        texts = self._to_list(text_input)
        processed_texts = []

        for text_tokens in self.tokenize(texts):
            tokens = [
                tok for tok in text_tokens if tok not in STOP_WORDS
            ]
            text = ' '.join(tokens)
            processed_texts.append(text)

        return processed_texts

    def remove_punctuation(self, text_input):
        punctuations = string.punctuation

        texts = self._to_list(text_input)
        processed_texts = []

        for text_tokens in self.tokenize(texts):
            tokens = [
                tok for tok in text_tokens if tok not in punctuations
            ]
            text = ' '.join(tokens)
            processed_texts.append(text)

        return processed_texts
