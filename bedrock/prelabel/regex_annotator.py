from bedrock.prelabel.findpattern import findpattern
from bedrock.prelabel.annotator_if import Annotator
from bedrock.doc.doc import Doc
import pandas as pd


class RegexAnnotator(Annotator):

    def __init__(self, patterns: dict):
        self._patterns = patterns

    def get_annotations(self, doc: Doc) -> (pd.DataFrame, pd.DataFrame):

        columns = ['beg', 'end', 'layer', 'feature', 'class', 'sofa_id'] # TODO needs to be changed
        annotations = pd.DataFrame(columns=columns)
        for key1, value in self._patterns.items():
            for key2, value2 in value.items():
                vec, match = findpattern(str(value2['regex']), doc.get_text())
                for v in vec:
                    annotations = annotations.append({
                        'beg': int(v[0]),
                        'end': int(v[1]),
                        'layer': 'custom',
                        'feature': value2['xmi_property'],
                        'feature_value': value2['tag_name'],
                    }, ignore_index=True)

        return annotations, None





