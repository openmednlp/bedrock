from bedrock.prelabel.findpattern import findpattern
from bedrock.prelabel.annotator_if import Annotator
from bedrock.doc.doc import Doc, Token, Annotation, Relation
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
                token_index = int(current_tokens[current_tokens[Token.ID] == row[Annotation.ID]].index[0])
                window_start_index = token_index - rule["window"] if index - rule["window"] >= 0 else 0
                window_end_index = token_index + rule["window"] if index + rule["window"] < len(current_annotations) else len(current_annotations) - 1

                window_tokens = current_tokens[window_start_index:window_end_index]
                annotations_in_window = current_annotations.loc[current_annotations[Annotation.ID].isin(window_tokens[Token.ID])]

        return current_annotations, current_relations





