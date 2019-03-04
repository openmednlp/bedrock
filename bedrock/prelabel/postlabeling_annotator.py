from bedrock.prelabel.annotator_if import Annotator
from bedrock.doc.doc import Doc, Token, Annotation
import pandas as pd


class PostlabelingAnnotator(Annotator):

    def __init__(self, rules: dict):
        self._rules = rules

    def get_annotations(self, doc: Doc) -> (pd.DataFrame, pd.DataFrame):

        current_tokens = doc.get_tokens()
        current_tokens = current_tokens[current_tokens[Token.POS_VALUE] != 'PUNCT']

        current_annotations = doc.get_annotations().copy()
        current_relations = doc.get_relations().copy()

        for rule in self._rules:
            rule_affected_annotations = current_annotations.copy()
            rule_required_annotations = current_annotations.copy()

            for ident in rule["identifier"]:
                rule_affected_annotations = rule_affected_annotations[rule_affected_annotations[ident["column"]] ==
                                                                      ident["value"]]
            for ident in rule["requires"]:
                rule_required_annotations = rule_required_annotations[rule_required_annotations[ident["column"]] ==
                                                                      ident["value"]]

            rule_affected_annotations["remove"] = False

            for _, rule_affected_annotation in rule_affected_annotations.iterrows():
                left_affected_tokens = current_tokens[current_tokens[Token.END] <=
                                                      rule_affected_annotation[Annotation.BEGIN]
                ].sort_values(by=Token.BEGIN, ascending=False).head(int(rule["window"]))
                right_affected_tokens = current_tokens[current_tokens[Token.BEGIN] >=
                                                      rule_affected_annotation[Annotation.END]
                ].sort_values(by=Token.BEGIN).head(int(rule["window"]))

                if "ignore_sentence_boundaries" not in rule or rule["ignore_sentence_boundaries"] is False:
                    print('ignore sentence boundaries')
                    # check if a sentence start flag is set in one of the windows
                    # TODO: remove the tokens over the sentence boundaries
                    # print('left', left_affected_tokens, 'right', right_affected_tokens)
                    # get_left_affected_tokens_sentence_start = left_affected_tokens[pd.notnull(left_affected_tokens[Token.SENT_START])] # & left_affected_tokens[Token.SENT_START] is True] #.sort_values(by=Token.END, ascending=False).head(1)
                    # get_right_affected_tokens_sentence_start = right_affected_tokens[pd.notnull(left_affected_tokens[Token.SENT_START])] # & right_affected_tokens[Token.SENT_START] is True] #.sort_values(by=Token.BEGIN).head(1)
                    # print('test_left', get_left_affected_tokens_sentence_start)
                    # print('test_right', get_right_affected_tokens_sentence_start)

                window_begin = left_affected_tokens.loc[left_affected_tokens[Token.BEGIN].idxmin()][Token.BEGIN]
                window_end = right_affected_tokens.loc[right_affected_tokens[Token.BEGIN].idxmax()][Token.END]
                print('begin', window_begin, 'end', window_end)

                print(rule_required_annotations[(rule_required_annotations[Annotation.BEGIN] >= window_begin) & (rule_required_annotations[Annotation.END] <= window_end)])

                rule_affected_annotation["remove"] = rule_required_annotations[
                                                         (rule_required_annotations[Annotation.BEGIN] >= window_begin) &
                                                         (rule_required_annotations[Annotation.END] <= window_end)
                                                     ].shape[0] > 0

            print(rule_affected_annotations)

        return current_annotations, current_relations
