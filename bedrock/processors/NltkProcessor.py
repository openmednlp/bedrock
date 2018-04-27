from bedrock.processors.Processor import Processor
from nltk import SnowballStemmer
from nltk import word_tokenize
from bedrock.processors.SpacyProcessor import SpacyProcessor
import nltk

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')


class NltkProcessor(Processor):
    def __init__(self, lang='de'):
        if lang == 'en':
            # TODO: test english
            raise NotImplementedError('Still not tested')
            # e.g. self.lemmatizer = WordNetLemmatizer().lemmatize

        elif lang == 'de':
            self.sentence_tokenizer = nltk.data.load('tokenizers/punkt/german.pickle')
        else:
            raise NotImplementedError(
                'lemmatizer for language \'{}\' not implemented'
                .format(lang)
            )

        self.stemmer = SnowballStemmer(self._lang_convert[lang])

    def lemmatize(self, text_input):
        # Lematize string or list of texts.
        # Always returns list of texts.
        print('No NLTK lemmatizer for German, using Spacy')

        p = SpacyProcessor('de')
        return p.lemmatize(text_input)

    def sentence_tokenize(self, text_input):
        texts = self._to_list(text_input)
        sentence_tokenized_texts = []
        for text in texts:
            sentences = self.sentence_tokenizer.tokenize(text)
            sentence_tokenized_texts.append(sentences)
        return sentence_tokenized_texts

    def stem(self, text_input):
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
        processed_texts = []
        for text in texts:
            tokenized_text = word_tokenize(text)
            processed_texts.append(tokenized_text)
        return processed_texts

    def remove_short(self, text_input, min_word_len):
        # TODO: tests and check
        # TODO: Can be abstracted, only tokenize calls are different

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
        raise NotImplementedError

    def remove_punctuation(self, text_input):
        raise NotImplementedError
