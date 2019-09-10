from bedrock.annotator.annotator import Annotator
from bedrock.doc.doc import Doc
from bedrock.doc.token import Token
from bedrock.doc.annotation import Annotation
from bedrock.doc.relation import Relation
from bedrock.doc.layer import Layer
from typing import List
import pandas as pd
from fuzzywuzzy import process
from fuzzywuzzy import fuzz
import _pickle as pickle
from typing import Callable
from bedrock.libs.CharSplit import char_split
from typing import Set
import warnings
import re


# DictionaryAnnotator is the actual implementation of the annotator. It searches terms in the dictionary in the
# sentences of a document and will give back a list of annotations and relations
class DictionaryAnnotator(Annotator):

    ROOT = 'root'
    TREE = 'tree'
    TERM = 'term'
    QUERY = 'query'
    LENGTH = 'length'
    SPLIT = 'split'
    ADDED = 'added'
    WORD = 'word'
    COUNT = 'count'
    SEP = ':'
    WHITESPACE = ' '

    def __init__(self, origin: str, layer_name: str = "", terms: List[str] = None, features: List[str] = None,
                 feature_values: List[str] = None, model_path: str = None, min_matching_score: int = 90,
                 word_basic_form_fn: Callable[[str], str] = lambda word: word, stop_words: Set = {}):

        if model_path is None and (len(terms) != len(feature_values) or len(feature_values) != len(features)):
            raise Exception('Lengths of terms, feature values and features vary.')

        if min_matching_score < 0 or min_matching_score > 100:
            warnings.warn('Minimum matching score have to be between 0 and 100: {}', min_matching_score)
            min_matching_score = 90

        self._min_matching_score = min_matching_score
        self._origin = origin
        self._layer_name = layer_name
        self._stemmer_fn = word_basic_form_fn
        self._stop_words = stop_words

        # create a new model if no path is given
        if model_path is None:
            self._data = pd.DataFrame(
                {
                    self.TERM: terms,
                    Annotation.FEATURE_VAL: feature_values,
                    Annotation.FEATURE: features
                }
            )
            self._features_values = feature_values
            self.__create_model()
        # load an model if the path is given
        else:
            with open(model_path, 'rb') as pickle_in:
                self._data, self._word_list = pickle.load(pickle_in)
                self._regex = re.compile('|'.join(map(re.escape, list(self._word_list[self.WORD]))), re.I)

    def __create_model(self):
        """ will create a list of words that occurs in the dictionary
        """
        self._data = self.__split_and_stem(self._data)

        word_list = pd.DataFrame(columns=[self.WORD, self.COUNT])

        for idx, row in self._data.iterrows():
            for word in row[self.SPLIT]:
                already_in = word_list[word_list[self.WORD] == word]
                if len(already_in.index) > 0:
                    word_list.loc[word_list[self.WORD] == word, self.COUNT] = word_list.loc[word_list[self.WORD] == word, self.COUNT] + 1
                else:
                    word_list = word_list.append({
                        self.WORD: word,
                        self.COUNT: 1
                    }, ignore_index=True)

        self._word_list = word_list
        self._regex = re.compile('|'.join(map(re.escape, list(self._word_list[self.WORD]))), re.I)

    # adds split column with split and stemmed terms
    def __split_and_stem(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        split_and_stem will split the terms in the dictionary to get words and stem them
        :param data: the data frame that contains the dictionary
        """
        # split the list by a whitespace char
        t = data[self.TERM].apply(lambda x: x.split(self.WHITESPACE))

        # remove words that are shorter or equal than 2 chars
        t = t.apply(lambda x: list(filter(lambda a: len(a) > 2, x)))

        # remove stop words
        t = t.apply(lambda x: list(filter(lambda a: a not in self._stop_words, x)))

        # split compounding words
        t = t.apply(lambda x: self.__split_compounds(x))

        # to lower case
        t = t.apply(lambda x: list(map(lambda a: a.lower(), x)))

        # find the stemming of the remaining words
        t = t.apply(lambda x: list(map(self._stemmer_fn, x)))
        data[self.SPLIT] = t
        data[self.QUERY] = data[self.SPLIT].apply(lambda x: self.WHITESPACE.join(x))
        data[self.LENGTH] = data[self.SPLIT].apply(lambda x: len(x))
        return data

    def __split_compounds(self, words: List[str]) -> List[str]:
        """
        split compounds will split a list of words into their compounds
        :param words: a list of strings
        """
        splitted_words = []

        while len(words) > 0:
            word = words.pop()
            if len(word) <= 6 or word[0].isupper() is False:
                splitted_words.append(word)
                continue
            rate, head, tail = char_split.split_compound(word)[0]
            if rate < 0.7:
                splitted_words.append(word)
                continue
            words.append(head)
            words.append(tail) 

        return splitted_words

    def __token_sorting_key(self, token):
        """
        token_sorting_key will return the field in a token to sort the tokens whereby
        :param token:
        :returns the begin field in a token
        """
        return token[Token.BEGIN]

    def save_model(self, path: str):
        """
        save model will store the model of the dictionary annotator to a given path
        :param path:
        """
        with open(path, 'wb') as pickle_file:
            pickle.dump([self._data, self._word_list], pickle_file)

    def get_min_matching_score(self):
        """
        get_min_matching_score will return the currently set minimum score
        :returns the set minimum matching score:
        """
        return self._min_matching_score

    def set_min_matching_score(self, score: int):
        """
        set_min_matching_score will overwrite the currently set minimum score
        :param the new minimum score:
        """
        self._min_matching_score = score

    def get_annotations(self, doc: Doc) -> (pd.DataFrame, pd.DataFrame):
        """
        get_annotations will find the given named entities of the dictionary in the doc text
        :param doc:
        :returns a tuple of dataframes, the first contains the annotations the second contains relations between annotations
        """
        old_annotations = doc.get_annotations()
        doc_text = doc.get_text()

        # prelabel all words that occurs in the dictionary
        matches = pd.DataFrame(columns=[Annotation.BEGIN, Annotation.END, self.QUERY])
        for match in self._regex.finditer(doc_text):
            matches = matches.append({
                Annotation.BEGIN: match.span()[0],
                Annotation.END: match.span()[1],
                self.QUERY: match.group()
            }, ignore_index=True)

        # initialize the new annotations and relations table
        new_annotations = pd.DataFrame(columns=Annotation.COLS)
        new_relations = pd.DataFrame(columns=Relation.COLS)

        # get all sentences from the document
        sentences = old_annotations[old_annotations[Annotation.LAYER] == Layer.SENTENCE]

        # if no sentences are available stop here, because we want to label labels in the dictionary on sentence level
        if sentences.empty:
            raise Exception('No sentences available')

        # iterate thru the sentences of a document to search for entities in the dictionary
        for index, sentence in sentences.iterrows():

            # get the beginning and the end of each sentence to search for prelabeled
            begin = sentence[Annotation.BEGIN]
            end = sentence[Annotation.END]

            # find all prelabeld words that are in the current sentence boundaries
            sentence_matches = matches[(matches[Annotation.BEGIN] >= begin) & (matches[Annotation.END] <= end)]

            matched_words_list = list(sentence_matches[self.QUERY])
            matched_word_string = self.WHITESPACE.join(matched_words_list)

            # find all entries in the dictionary that have at most as many words as the number of prelabeled
            # words in the sentence
            filtered_data = self._data[self._data[self.LENGTH] <= len(matched_words_list)]

            # create a dict to search in for the fuzzywuzzy library
            data_index = list(filtered_data.index)
            data_queries = list(filtered_data[self.QUERY])

            #
            queries = dict(zip(data_index, data_queries))
            fuzzy_matches = process.extractWithoutOrder(matched_word_string, queries, scorer=fuzz.token_set_ratio,
                                                        score_cutoff=self._min_matching_score)

            # create a dict that holds all found entities in a sentence
            sentence_index = sentence_matches[Annotation.BEGIN].map(str) + ':' + sentence_matches[Annotation.END].map(str)
            sentence_queries = dict(zip(sentence_index, matched_words_list))

            for span, score, idx in fuzzy_matches:
                words = span.split(self.WHITESPACE)

                # initialize the old index for assigning relations correctly
                old_index = 0

                # iterate over all words in the match
                for word_index, word in enumerate(words):

                    # for each word in the match find the corresponding word in the sentence
                    word_match = process.extractOne(word, sentence_queries)

                    # get the begin and end value of the key
                    begin = int(word_match[2].split(self.SEP)[0])
                    end = int(word_match[2].split(self.SEP)[0])

                    # append new annotation
                    new_annotations = new_annotations.append({
                        Annotation.BEGIN: begin,
                        Annotation.END: end,
                        Annotation.LAYER: self._layer_name,
                        Annotation.FEATURE:  filtered_data.loc[idx][Annotation.FEATURE],
                        Annotation.FEATURE_VAL: filtered_data.loc[idx][Annotation.FEATURE_VAL]
                    }, ignore_index=True)

                    # set the current annotation id for the relation
                    current_idx = max(list(new_annotations.index.values))

                    # if we have more than one word in the dictionary connect them via relations
                    if len(words) > 1 and word_index > 0:
                        new_relations = new_relations.append({
                            Relation.GOV_ID: old_index,
                            Relation.DEP_ID: current_idx,
                            Relation.LAYER: self._layer_name,
                            Relation.BEGIN: begin,
                            Relation.END: end,
                            Relation.FEATURE: filtered_data.loc[idx][Annotation.FEATURE],
                            Relation.FEATURE_VAL: filtered_data.loc[idx][Annotation.FEATURE_VAL]
                        }, ignore_index=True)

                    old_index = current_idx

        return new_annotations, new_relations
