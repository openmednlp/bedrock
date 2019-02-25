from bedrock.prelabel.findpattern import findpattern
from bedrock.prelabel.annotator_if import Annotator
from bedrock.doc.doc import Doc
import pandas as pd


class PostlabelingAnnotator(Annotator):

    def __init__(self, rules: dict):
        self._rules = rules

    def get_annotations(self, doc: Doc) -> (pd.DataFrame, pd.DataFrame):

        current_tokens = doc.get_tokens()
        current_annotations = doc.get_annotations().copy()
        current_relations = doc.get_relations().copy()

        for rule in self._rules:
            rule_affected_annotations = current_annotations[current_annotations[rule["column_identifier"]] == rule["column_value"]]

            for index, row in rule_affected_annotations.iterrows():
                window_start_index = index - rule["window"] if index - rule["window"] >= 0 else 0
                window_end_index = index + rule["window"] if index + rule["window"] < len(current_annotations) else len(current_annotations) - 1


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





