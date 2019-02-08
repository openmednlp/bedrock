from bedrock.prelabel.labeler_if import Labeler
from bedrock.doc.doc_if import Doc
import pandas as pd
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from fuzzysearch import find_near_matches


class DictionaryLabeler(Labeler):

    def __init__(self, dictionary: pd.DataFrame):
        self._dictionary = dictionary

    def get_labels(self, doc: Doc) -> pd.DataFrame:

        columns = ['beg', 'end', 'layer', 'feature', 'class', 'sofa_id']
        labels = pd.DataFrame(columns=columns)

        annotations = doc.get_annotations()
        sentences = annotations[annotations['feature'] == 'sentence']
        if sentences.empty:
            raise Exception('No sentences available')

        queries = self._dictionary['term']
        codes = self._dictionary['referencedComponentId']

        for index, sentence in sentences.iterrows():

            begin = sentence['beg']
            end = sentence['end']
            text = doc.get_text()[begin:end]

            for word, _, _ in process.extractBests(text, queries, scorer=fuzz.token_set_ratio, score_cutoff=86, limit=len(text)):
                matches = find_near_matches(word, text, max_l_dist=2)
                index = queries[queries == word].index[0]
                code = codes[index]
                for match in matches:
                    labels = labels.append({
                        'beg': begin + match.start,
                        'end': end + match.end,
                        'layer': 'custom',
                        'feature': 'Morphology',
                        'class': code,
                        'sofa_id': 0  # TODO sofa_id??
                    }, ignore_index=True)

        return labels
