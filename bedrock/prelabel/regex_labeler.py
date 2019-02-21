from bedrock.prelabel.findpattern import findpattern
from bedrock.prelabel.labeler_if import Labeler
from bedrock.doc.doc import Doc
import pandas as pd


class RegexLabeler(Labeler):

    def __init__(self, patterns: dict):
        self._patterns = patterns

    def get_labels(self, doc: Doc) -> pd.DataFrame:

        labels = pd.DataFrame()
        for key1, value in self._patterns.items():
            for key2, value2 in value.items():
                vec, match = findpattern(str(value2['regex']), doc.get_text())
                for v in vec:
                    labels = labels.append({
                        'begin': int(v[0]),
                        'end': int(v[1]),
                        'layer': 'custom',
                        'feature': value2['xmi_property'],
                        'feature_value': value2['tag_name'],
                    }, ignore_index=True)

        return labels





