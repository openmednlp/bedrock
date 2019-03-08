from bedrock.prelabel.findpattern import find_regex_pattern
from bedrock.prelabel.annotator import Annotator
from bedrock.doc.doc import Doc
from doc.annotation import Annotation
from doc.token import Token
import pandas as pd


class RegexAnnotator(Annotator):

    def __init__(self, patterns: dict, layer_name: str):
        self.__patterns = patterns
        self.__layer_name = layer_name

    def get_annotations(self, doc: Doc) -> (pd.DataFrame, pd.DataFrame):

        tokens = doc.get_tokens().copy()

        annotations = pd.DataFrame()
        for key1, value in self.__patterns.items():
            for key2, value2 in value.items():
                vec, match = find_regex_pattern(str(value2['regex']), doc.get_text())
                for v in vec:
                    begin = int(v[0])
                    end = int(v[1])

                    # find the token matching the regular expresssion
                    token = tokens[(tokens[Token.BEGIN] >= begin) & (tokens[Token.END] <= end)]
                    if token.empty:
                        continue

                    annotations = annotations.append({
                        Annotation.ID: token[Token.ID].iloc[0],
                        Annotation.BEGIN: token[Token.BEGIN].iloc[0],
                        Annotation.END: token[Token.END].iloc[0],
                        Annotation.LAYER: self.__layer_name,
                        Annotation.FEATURE: value2['xmi_property'],
                        Annotation.FEATURE_VAL: value2['tag_name'],
                    }, ignore_index=True)

        return annotations, None
