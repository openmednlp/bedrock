from bedrock.prelabel.findpattern import find_regex_pattern
from bedrock.prelabel.annotator_if import Annotator
from bedrock.doc.doc import Doc
from doc.annotation import Annotation
import pandas as pd


class RegexAnnotator(Annotator):

    def __init__(self, patterns: dict, layer_name: str):
        self.__patterns = patterns
        self.__layer_name = layer_name

    def get_annotations(self, doc: Doc) -> pd.DataFrame:

        labels = pd.DataFrame()
        for key1, value in self.__patterns.items():
            for key2, value2 in value.items():
                vec, match = find_regex_pattern(str(value2['regex']), doc.get_text())
                for v in vec:
                    labels = labels.append({
                        Annotation.BEGIN: int(v[0]),
                        Annotation.END: int(v[1]),
                        Annotation.LAYER: self.__layer_name,
                        Annotation.FEATURE: value2['xmi_property'],
                        Annotation.FEATURE_VAL: value2['tag_name'],
                    }, ignore_index=True)

        return labels





