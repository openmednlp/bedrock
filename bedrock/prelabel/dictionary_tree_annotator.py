from bedrock.prelabel.annotator_if import Annotator
from bedrock.doc.doc import Doc
from typing import List
from functools import reduce
import pandas as pd
from fuzzywuzzy import process
from fuzzywuzzy import fuzz
from nltk.stem.cistem import Cistem


class Node:
    def __init__(self, term: str, parent):
        self._term = term
        self._parent = parent
        self._classes = list()
        self._children = list()
        self._stemmed_children = {}

    def add_child(self, node):
        self._stemmed_children[len(self._children)] = node.get_term()
        self._children.append(node)

    def add_class(self, class_code: str, feature: str):
        # avoid duplicates
        class_object = {'class': class_code, 'feature': feature}
        if class_object not in self._classes:
            self._classes.append(class_object)

    def get_term(self):
        return self._term

    def get_children(self):
        return self._children

    def get_stemmed_children(self):
        return self._stemmed_children

    def get_parent(self):
        return self._parent

    def get_classes(self):
        return self._classes

    def print_tree(self, depth):
        separator = ''
        if depth > 0:
            separator += '+ '
        for i in range(depth):
            separator += '- '
        print(separator, sep='', end='', flush=True)
        if not self._classes:
            print(self._term, sep='', end='\n', flush=True)
        if self._classes:
            print(self._term + ' ', sep='', end='', flush=True)
            print(self._classes, sep='', end='\n', flush=True)
        if not self._children:
            return
        for child in self._children:
            # text += '-' + child.get_term() + '\n'
            child.print_tree(depth + 1)
        return

    def print(self):
        self.print_tree(0)


class DictionaryTreeLabeler(Annotator):

    def __init__(self, terms: List[str], classes: List[str], features: List[str], origin: str):
        if len(terms) != len(classes) or len(classes) != len(features):
            raise Exception('Lengths of terms, classes and features vary.')
        self._origin = origin
        self._data = pd.DataFrame(
            {
                'term': terms,
                'class': classes,
                'feature': features
            }
        )
        self._classes = classes
        self._stemmer = Cistem()
        self._tree = Node('root', None)
        self.__create_tree()

    def __create_tree(self):
        self.__split_and_stem(self._data)

        max_length = self._data['length'].max()

        for length in range(max_length):
            list_with_length = self._data[self._data['length'] == length + 1]

            for index, row in list_with_length.iterrows():
                not_added = row['length']
                current_tree = self._tree

                # add all terms that are not added to the tree
                while not_added > 0:

                    # flag if a new term was found in the current subtree
                    term_found = False

                    # search if any node is added to the current subtree
                    for term in row['split']:

                        # if the term is already added, jump over it
                        if term["added"] is True:
                            continue

                        for child in current_tree.get_children():
                            if fuzz.ratio(child.get_term(), term["term"]) >= 75:
                                term_found = True
                                term["added"] = True
                                current_tree = child
                                break

                    # if no more terms are found in the subtree add
                    # all other terms to the tree
                    if term_found is False:
                        for term in row['split']:
                            if term["added"] is True:
                                continue
                            node = Node(term["term"], current_tree)
                            current_tree.add_child(node)
                            current_tree = node
                            term["added"] = True

                    not_added = reduce(lambda x, y: x + 1 if y['added'] is False else x, row['split'], 0)

                    # if all terms are added to the tree the hole term is on the tree, so mark the current
                    # node with the class
                    if not_added == 0:
                        current_tree.add_class(row['class'], row['feature'])

        # self._tree.print()

    # adds split column with split and stemmed terms
    def __split_and_stem(self, data: pd.DataFrame):
        # split the list by a whitespace char
        t = data['term'].apply(lambda x: x.split(' '))

        # remove words that are shorter or equal than 3 chars
        t = t.apply(lambda x: list(filter(lambda a: len(a) > 3, x)))

        # find the stemming of the remaining words
        t = t.apply(lambda x: list(map(self._stemmer.stem, x)))
        t = t.apply(lambda x: list(map(lambda a: {'term': a, 'added': False}, x)))
        data['split'] = t
        data['length'] = data['split'].apply(lambda x: len(x))

    def __token_sorting_key(self, token):
        return token['beg']

    def get_annotations(self, doc: Doc) -> (pd.DataFrame, pd.DataFrame):

        annotations = doc.get_annotations()
        sentences = annotations[annotations['layer'] == 'sentence']

        new_annotations = pd.DataFrame(columns=['begin', 'end', 'layer', 'feature', 'feature_value'])
        new_relations = pd.DataFrame(columns=['governor_id', 'dependent_id', 'begin', 'end', 'layer'])

        if sentences.empty:
            raise Exception('No sentences available')

        for index, sentence in sentences.iterrows():

            begin = sentence['beg']
            end = sentence['end']
            sentence_tokens = doc.get_tokens()[(doc.get_tokens()['begin'] >= begin) & (doc.get_tokens()['end'] <= end) & (doc.get_tokens()['pos_value'] != 'PUNCT')]

            nodes_to_visit = list()
            nodes_to_visit.append({'tree': self._tree, 'path': None})

            while nodes_to_visit:

                current_node = nodes_to_visit.pop()
                current_path = list()
                if current_node['path'] is not None:
                    current_path = current_node['path']

                if current_node['tree'].get_classes():
                    for current_class in current_node['tree'].get_classes():
                        last_id = None
                        current_path.sort(key=self.__token_sorting_key)
                        for idx, token in enumerate(current_path):
                            new_annotations = new_annotations.append({
                                'begin': token['begin'],
                                'end': token['end'],
                                'layer': 'custom',
                                'feature': current_class['feature'],
                                'feature_value': current_class['class']
                            }, ignore_index=True)
                            if len(current_path) > 1 and idx > 0:
                                new_relations = new_relations.append({
                                    'governant_id': idx,
                                    'dependent_id': last_id,
                                    'begin': token['begin'],
                                    'end': token['end'],
                                    'layer': 'custom'
                                }, ignore_index=True)

                            last_id = idx

                for sentence_index, sentence_token_row in sentence_tokens.iterrows():
                    text = self._stemmer.stem(sentence_token_row['text'])
                    min_score_cutoff = 100 if len(text) < 4 else 80
                    match = process.extractOne(text, current_node['tree'].get_stemmed_children(),
                                               score_cutoff=min_score_cutoff - 1)
                    if match is None:
                        continue

                    path = [i for i in current_path]
                    path.append(sentence_token_row)

                    match_index = match[2]
                    nodes_to_visit.append({'tree': current_node['tree'].get_children()[match_index], 'path': path})

        return new_annotations, new_relations
