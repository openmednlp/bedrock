from bedrock.prelabel.annotator import Annotator
from bedrock.doc.doc import Doc, Token, Annotation, Relation, Layer
from typing import List
from functools import reduce
import pandas as pd
from fuzzywuzzy import process
from fuzzywuzzy import fuzz
from nltk.stem.cistem import Cistem


# Node class to generate a tree of words to reduce the search space, e.g. if we have to search for the terms
# 'small eyes' and 'small ears', and the algorithm could not find small in a sentence, all dictionary entries with
# that contains 'small' will be pruned from the tree
class Node:
    def __init__(self, term: str, parent):
        """ constructor
            term is a single word that occurs in the dictionary
            parent is None for the root node or the parent node for any other node in the tree
        """
        self._term = term
        self._parent = parent

        # initialize all features that should be annotated on the given term
        self._features = list()

        # all child nodes of the current node, the list is empty for leave nodes
        self._children = list()

        # a list of the terms of the children of the node
        self._stemmed_children = {}

    def add_child(self, node):
        """ add_child gets a new node as parameter and add it to the list of child nodes
        """
        self._stemmed_children[len(self._children)] = node.get_term()
        self._children.append(node)

    def add_feature(self, feature: str, feature_value: str):
        """ add_feature adds a feature to the list of feature values
        """
        feature_object = {Annotation.FEATURE_VAL: feature_value, Annotation.FEATURE: feature}
        # avoid duplicates
        if feature_object not in self._features:
            self._features.append(feature_object)

    def get_term(self):
        return self._term

    def get_children(self):
        return self._children

    def get_stemmed_children(self):
        return self._stemmed_children

    def get_parent(self):
        return self._parent

    def get_features(self):
        return self._features

    def print_tree(self, depth):
        """ depth-first-search algorithm to print out the tree nodes
        """
        separator = ''
        if depth > 0:
            separator += '+ '
        for i in range(depth):
            separator += '- '
        print(separator, sep='', end='', flush=True)
        if not self._features:
            print(self._term, sep='', end='\n', flush=True)
        if self._features:
            print(self._term + ' ', sep='', end='', flush=True)
            print(self._features, sep='', end='\n', flush=True)
        if not self._children:
            return
        for child in self._children:
            child.print_tree(depth + 1)
        return

    def print(self):
        """ print will print the term of the node and all nodes down in a depth-first-search manner
        """
        self.print_tree(0)


# DictionaryTreeAnnotator is the actual implementation of the annotator. It searches terms in the dictionary in the
# sentences of a document and will give back a list of annotations and relations
class DictionaryTreeAnnotator(Annotator):

    ROOT = 'root'
    TREE = 'tree'
    TERM = 'term'
    LENGTH = 'length'
    SPLIT = 'split'
    ADDED = 'added'
    PATH = 'path'

    def __init__(self, terms: List[str], features: List[str], feature_values: List[str], origin: str):
        if len(terms) != len(feature_values) or len(feature_values) != len(features):
            raise Exception('Lengths of terms, feature values and features vary.')
        self._origin = origin
        self._data = pd.DataFrame(
            {
                self.TERM: terms,
                Annotation.FEATURE_VAL: feature_values,
                Annotation.FEATURE: features
            }
        )
        self._features_values = feature_values
        self._stemmer = Cistem()
        self._tree = Node(self.ROOT, None)
        self.__create_tree()

    def __create_tree(self):
        """ create_tree will establish the tree for more efficient term searching
        """
        self.__split_and_stem(self._data)

        max_length = self._data[self.LENGTH].max()

        for length in range(max_length):
            list_with_length = self._data[self._data[self.LENGTH] == length + 1]

            for index, row in list_with_length.iterrows():
                not_added = row[self.LENGTH]
                current_tree = self._tree

                # add all terms that are not added to the tree
                while not_added > 0:

                    # flag if a new term was found in the current subtree
                    term_found = False

                    # search if any node is added to the current subtree
                    for term in row[self.SPLIT]:

                        # if the term is already added, jump over it
                        if term[self.ADDED] is True:
                            continue

                        for child in current_tree.get_children():
                            if fuzz.ratio(child.get_term(), term[self.TERM]) >= 75:
                                term_found = True
                                term[self.ADDED] = True
                                current_tree = child
                                break

                    # if no more terms are found in the subtree add
                    # all other terms to the tree
                    if term_found is False:
                        for term in row[self.SPLIT]:
                            if term[self.ADDED] is True:
                                continue
                            node = Node(term[self.TERM], current_tree)
                            current_tree.add_child(node)
                            current_tree = node
                            term[self.ADDED] = True

                    not_added = reduce(lambda x, y: x + 1 if y[self.ADDED] is False else x, row[self.SPLIT], 0)

                    # if all terms are added to the tree the hole term is on the tree, so mark the current
                    # node with the feature
                    if not_added == 0:
                        current_tree.add_feature(row[Annotation.FEATURE], row[Annotation.FEATURE_VAL])

        self._tree.print()

    # adds split column with split and stemmed terms
    def __split_and_stem(self, data: pd.DataFrame):
        """
        split_and_stem will split the terms in the dictionary to get words and stem them
        :param data: the dataframe that contains the dictionary
        """
        # split the list by a whitespace char
        t = data[self.TERM].apply(lambda x: x.split(' '))

        # remove words that are shorter or equal than 3 chars
        t = t.apply(lambda x: list(filter(lambda a: len(a) > 3, x)))

        # find the stemming of the remaining words
        t = t.apply(lambda x: list(map(self._stemmer.stem, x)))
        t = t.apply(lambda x: list(map(lambda a: {self.TERM: a, self.ADDED: False}, x)))
        data[self.SPLIT] = t
        data[self.LENGTH] = data[self.SPLIT].apply(lambda x: len(x))

    def __token_sorting_key(self, token):
        """
        token_sorting_key will return the field in a token to sort the tokens whereby
        :param token:
        :returns the begin field in a token
        """
        return token[Token.BEGIN]

    def get_annotations(self, doc: Doc) -> (pd.DataFrame, pd.DataFrame):

        annotations = doc.get_annotations()

        # get all sentences from the document
        sentences = annotations[annotations[Annotation.LAYER] == Layer.SENTENCE]

        # initialize the new annotations and relations table
        new_annotations = pd.DataFrame(columns=Annotation.COLS)
        new_relations = pd.DataFrame(columns=Relation.COLS)

        if sentences.empty:
            raise Exception('No sentences available')

        for index, sentence in sentences.iterrows():

            # get all tokens in a sentence that are not punctuation
            begin = sentence[Annotation.BEGIN]
            end = sentence[Annotation.END]
            sentence_tokens = doc.get_tokens()[(doc.get_tokens()[Token.BEGIN] >= begin) &
                                               (doc.get_tokens()[Token.END] <= end) &
                                               (doc.get_tokens()[Token.POS_VALUE] != 'PUNCT')]

            nodes_to_visit = list()
            nodes_to_visit.append({self.TREE: self._tree, self.PATH: None})

            while nodes_to_visit:

                current_node = nodes_to_visit.pop()
                current_path = list()
                if current_node[self.PATH] is not None:
                    current_path = current_node[self.PATH]

                # if the current node contains any feature_values, add all of them to the annotations table
                if current_node[self.TREE].get_features():
                    for current_feature in current_node[self.TREE].get_features():
                        last_id = None
                        current_path.sort(key=self.__token_sorting_key)
                        for idx, token in enumerate(current_path):
                            new_annotations = new_annotations.append({
                                Annotation.ID: token[Token.ID],
                                Annotation.BEGIN: token[Token.BEGIN],
                                Annotation.END: token[Token.END],
                                Annotation.LAYER: Layer.TUMOR,
                                Annotation.FEATURE: current_feature[Annotation.FEATURE],
                                Annotation.FEATURE_VAL: current_feature[Annotation.FEATURE_VAL]
                            }, ignore_index=True)
                            if len(current_path) > 1 and idx > 0:
                                new_relations = new_relations.append({
                                    Relation.GOV_ID: token[Token.ID],
                                    Relation.DEP_ID: last_id,
                                    Relation.BEGIN: token[Token.BEGIN],
                                    Relation.FEATURE: current_feature[Annotation.FEATURE],
                                    Relation.FEATURE_VAL: current_feature[Annotation.FEATURE_VAL]
                                }, ignore_index=True)

                            last_id = token[Token.ID]

                for sentence_index, sentence_token_row in sentence_tokens.iterrows():
                    text = self._stemmer.stem(sentence_token_row[Token.TEXT])

                    # for short words the comparison score has to be higher than for long words
                    min_score_cutoff = 100 if len(text) < 4 else 80

                    # get all children that has matches
                    match = process.extractOne(text, current_node[self.TREE].get_stemmed_children(),
                                               score_cutoff=min_score_cutoff - 1)

                    # if no match was found test the next sentence
                    if match is None:
                        continue

                    # if a match was found copy the current path and add the own token to it
                    path = [i for i in current_path]
                    path.append(sentence_token_row)

                    # get the index in the datatable of the match
                    match_index = match[2]
                    nodes_to_visit.append({self.TREE: current_node[self.TREE].get_children()[match_index],
                                           self.PATH: path})

        return new_annotations, new_relations
