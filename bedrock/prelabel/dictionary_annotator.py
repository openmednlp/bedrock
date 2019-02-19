from bedrock.prelabel.annotator_if import Annotator
from bedrock.doc.doc_if import Doc
from typing import List
import pandas as pd
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from fuzzysearch import find_near_matches


class DictionaryAnnotator(Annotator):

    def __init__(self, terms: List[str], classes: List[str], origin: str):
        self._origin = origin
        self._terms = terms
        self._classes = classes

    def get_annotations(self, doc: Doc) -> (pd.DataFrame, pd.DataFrame):

        columns = ['beg', 'end', 'layer', 'feature', 'class', 'sofa_id']
        annotations = pd.DataFrame(columns=columns)

        current_annotations = doc.get_annotations()
        sentences = current_annotations[current_annotations['feature'] == 'sentence']
        if sentences.empty:
            raise Exception('No sentences available')

        for index, sentence in sentences.iterrows():

            begin = sentence['beg']
            end = sentence['end']
            text = doc.get_text()[begin:end]

            for word, _, _ in process.extractBests(text, self._terms, scorer=fuzz.token_set_ratio, score_cutoff=86, limit=len(text)):
                word_length = len(word)
                matches = find_near_matches(word, text, max_deletions=round(word_length / 10), max_insertions=round(word_length / 10), max_substitutions=round(word_length / 4))
                index = self._terms.index(word)
                code = self._classes[index]
                for match in matches:
                    annotations = annotations.append({
                        'beg': begin + match.start,
                        'end': begin + match.end,
                        'layer': 'custom',
                        'feature': 'Morphology',
                        'class': code,
                        'origin': self._origin,
                        'sofa_id': 0  # TODO sofa_id??
                    }, ignore_index=True)

        return annotations, None
