from bedrock.prelabel.findpattern import findpattern
from bedrock.prelabel.labeler_if import Labeler
from bedrock.doc.doc_if import Doc
import pandas as pd


class RegexLabeler(Labeler):

    def __init__(self, patterns: dict):
        self._patterns = patterns

    def get_labels(self, doc: Doc) -> pd.DataFrame:

        columns = ['beg', 'end', 'layer', 'feature', 'class', 'sofa_id']
        labels = pd.DataFrame(columns=columns)
        for key1, value in self._patterns.items():
            for key2, value2 in value.items():
                vec, match = findpattern(str(value2['regex']), doc.get_text())
                for v in vec:
                    labels = labels.append({
                        'beg': int(v[0]),
                        'end': int(v[1]),
                        'layer': 'custom',
                        'feature': value2['xmi_property'],
                        'class': value2['tag_name'],
                        'sofa_id': 0  # TODO sofa_id??
                    }, ignore_index=True)

        return labels





