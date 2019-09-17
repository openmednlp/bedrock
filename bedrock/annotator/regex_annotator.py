from bedrock.annotator.annotator import Annotator
from bedrock.doc.doc import Doc
from bedrock.doc.annotation import Annotation
import pandas as pd
import re


class RegexAnnotator(Annotator):

    def __init__(self, patterns: dict, layer_name: str):
        self.__patterns = patterns
        self.__layer_name = layer_name

    def _find_regex_pattern(regex, text):
        reg = re.compile(regex)
        vec = []
        match = []
        string = ''

        for el in re.finditer(reg, text):
            if el:
                indices = el.span()
                vec.append(indices)
                match.append(el.group())
                string = string + text[indices[0]:indices[1]] + ', '
        return vec, match

    def get_annotations(self, doc: Doc) -> (pd.DataFrame, pd.DataFrame):
        annotations = pd.DataFrame()
        relations = pd.DataFrame()
        for key1, value in self.__patterns.items():
            for key2, value2 in value.items():
                vec, match = self._find_regex_pattern(str(value2['regex']), doc.get_text())
                for v in vec:
                    begin = int(v[0])
                    end = int(v[1])

                    annotations = annotations.append({
                        Annotation.BEGIN: begin,
                        Annotation.END: end,
                        Annotation.LAYER: self.__layer_name,
                        Annotation.FEATURE: value2['xmi_property'],
                        Annotation.FEATURE_VAL: value2['tag_name'],
                    }, ignore_index=True)

        return annotations, relations
