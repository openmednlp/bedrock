from bedrock.prelabel.annotator_if import Annotator
from bedrock.doc.doc import Doc
import pandas as pd
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from fuzzysearch import find_near_matches


class DictionaryAnnotator(Annotator):

    def __init__(self, dictionary: pd.DataFrame):
        self._dictionary = dictionary

    def get_labels(self, doc: Doc) -> pd.DataFrame:

        columns = ['begin', 'end', 'layer', 'feature', 'feature_value']
        labels = pd.DataFrame(columns=columns)

        annotations = doc.get_annotations()
        sentences = annotations[annotations['layer'] == 'sentence']
        if sentences.empty:
            raise Exception('No sentences available')

        queries = self._dictionary['term']
        codes = self._dictionary['referencedComponentId']

        for index, sentence in sentences.iterrows():

            begin = sentence['begin'].astype(int)
            end = sentence['end'].astype(int)
            text = doc.get_text()[begin:end]

            for word, _, _ in process.extractBests(text, queries, scorer=fuzz.token_set_ratio, score_cutoff=86, limit=len(text)):
                matches = find_near_matches(word, text, max_l_dist=2)
                index = queries[queries == word].index[0]
                code = codes[index]
                for match in matches:
                    labels = labels.append({
                        'begin': begin + match.start,
                        'end': end + match.end,
                        'layer': 'custom',
                        'feature': 'Morphology',
                        'feature_value': code,
                    }, ignore_index=True)

        return labels
