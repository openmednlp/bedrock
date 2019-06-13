from bedrock.annotator.dictionary_annotator import DictionaryAnnotator
from typing import List
import pandas as pd


# NegationAnnotator is a specific implementation of the DictionaryAnnotator to detect negations in german and/or english
class NegationAnnotator(DictionaryAnnotator):
    def __init__(self, origin: str, layer_name: str, language_code: str = 'de', terms: List[str] = None,
                 features: List[str] = None, feature_values: List[str] = None):
        negation_list = None
        if language_code == "de":
            negation_list = pd.read_csv("./negation_de.csv", sep="\t")
            terms = negation_list["term"].tolist()
            features = negation_list["feature"].tolist()
            feature_values = negation_list["feature_value"].tolist()
        elif language_code == "en":
            negation_list = pd.read_csv("./negation_en.csv", sep="\t")
            terms = negation_list["term"].tolist()
            features = negation_list["feature"].tolist()
            feature_values = negation_list["feature_value"].tolist()
        elif negation_list is None and (terms is None or features is None or feature_values is None):
            raise Exception("language not supported yet, provide terms, features and feature_values")
        DictionaryAnnotator.__init__(origin, layer_name, terms, features, feature_values)