from bedrock.annotator.annotator import Annotator
from bedrock.doc.doc import Doc, Token, Annotation, Relation
import pandas as pd


class PostlabelingAnnotator(Annotator):

    IDENTIFIER = 'identifier'
    PUNCTUATION = 'PUNCT'
    REQUIRES = 'requires'
    COLUMN = 'column'
    VALUE = 'value'
    LEAVE = 'leave'
    IGNORE_SENTENCE_BOUNDARIES = 'ignore_sentence_boundaries'
    WINDOW = 'window'
    LEFT_WINDOW = 'left_window'
    RIGHT_WINDOW = 'right_window'

    def __init__(self, rules: dict):
        self._rules = rules

    def get_annotations(self, doc: Doc) -> (pd.DataFrame, pd.DataFrame):

        # get the tokens of the doc and remove all punctuation
        current_tokens = doc.get_tokens()
        current_tokens = current_tokens[current_tokens[Token.POS_VALUE] != self.PUNCTUATION]

        # create a copy of the documents annotations and relations
        current_annotations = doc.get_annotations().copy()
        current_relations = doc.get_relations().copy()

        annotations_to_hold = pd.DataFrame()

        # apply all rules
        for rule in self._rules:

            # get all annotations that could be affected by a rule
            rule_affected_annotations = current_annotations.copy()
            rule_required_annotations = current_annotations.copy()

            # identify the affected annotations
            for ident in rule[self.IDENTIFIER]:
                rule_affected_annotations = rule_affected_annotations[rule_affected_annotations[ident[self.COLUMN]] ==
                                                                      ident[self.VALUE]]
            for ident in rule[self.REQUIRES]:
                rule_required_annotations = rule_required_annotations[rule_required_annotations[ident[self.COLUMN]] ==
                                                                      ident[self.VALUE]]

            # set the leave flag that indicates the annotation should
            rule_affected_annotations[self.LEAVE] = False

            for annotation_index, rule_affected_annotation in rule_affected_annotations.iterrows():

                # --- find the tokens left and right of the annotation to specify the window ---
                left_affected_tokens = current_tokens[current_tokens[Token.END] <=
                                                      rule_affected_annotation[Annotation.BEGIN]
                ].sort_values(by=Token.BEGIN, ascending=False).head(int(rule[self.WINDOW]))
                right_affected_tokens = current_tokens[current_tokens[Token.BEGIN] >=
                                                      rule_affected_annotation[Annotation.END]
                ].sort_values(by=Token.BEGIN).head(int(rule[self.WINDOW]))

                if left_affected_tokens.empty and right_affected_tokens.empty:
                    continue

                # check if the right or left window is empty
                if left_affected_tokens.empty and right_affected_tokens.empty is False:
                    window_begin = rule_affected_annotation[Annotation.BEGIN]
                    window_end = right_affected_tokens.loc[right_affected_tokens[Token.BEGIN].idxmax()][Token.END]
                elif left_affected_tokens.empty is False and right_affected_tokens.empty:
                    window_begin = left_affected_tokens.loc[left_affected_tokens[Token.BEGIN].idxmin()][Token.BEGIN]
                    window_end = rule_affected_annotation[Annotation.END]
                else:
                    window_begin = left_affected_tokens.loc[left_affected_tokens[Token.BEGIN].idxmin()][Token.BEGIN]
                    window_end = right_affected_tokens.loc[right_affected_tokens[Token.BEGIN].idxmax()][Token.END]

                # if the sentence boundaries should not be ignored, we have to find them
                if self.IGNORE_SENTENCE_BOUNDARIES not in rule or rule[self.IGNORE_SENTENCE_BOUNDARIES] is False:
                    sentence_bound_left = left_affected_tokens.loc[left_affected_tokens[Token.SENT_START] == True]
                    if sentence_bound_left.empty is False:
                        window_begin = sentence_bound_left.loc[sentence_bound_left[Token.BEGIN].idxmax()][Token.BEGIN]

                    sentence_bound_right = right_affected_tokens.loc[right_affected_tokens[Token.SENT_START] == True]
                    if sentence_bound_right.empty is False:
                        window_end = sentence_bound_right.loc[sentence_bound_right[Token.BEGIN].idxmin()][Token.BEGIN]

                    test = rule_required_annotations[
                                (rule_required_annotations[Annotation.BEGIN] >= window_begin) &
                                (rule_required_annotations[Annotation.END] <= window_end)
                            ].shape[0] > 0

                    rule_affected_annotations.loc[annotation_index, self.LEAVE] = test > 0

            annotations_to_hold = annotations_to_hold.append(rule_affected_annotations)

        # all annotation that fulfil the required rule
        annotations_ids_to_stay = annotations_to_hold[annotations_to_hold[self.LEAVE] == True].index.tolist()

        # all annotations that are affected by the rule but do not fulfil it
        annotations_ids_to_remove = list(set(rule_affected_annotations.index.tolist()) -
                                         set(annotations_ids_to_stay))

        # filter out all annotations their id is in the annotations to remove list
        current_annotations.drop(index=annotations_ids_to_remove, inplace=True)

        # filter out all relations that are based on a remove annotation
        remove_relations = current_relations[Relation.GOV_ID].isin(annotations_ids_to_remove) |\
                           current_relations[Relation.DEP_ID].isin(annotations_ids_to_remove)
        new_relations = current_relations[remove_relations == False]

        return current_annotations, new_relations
