import pandas as pd
import html
from bedrock.doc.relation import Relation
from bedrock.doc.annotation import Annotation
from bedrock.doc.token import Token
from bedrock.doc.layer import Layer
from bedrock.common import uima
import logging
from typing import Any
import warnings



class CAS2DataFrameConverter:

    def __init__(self, mapping_fns: dict = None, appending_fns: dict = None):
        if mapping_fns is None:
            self.__mapping_fns = {}
        else:
            self.__mapping_fns = mapping_fns

        if appending_fns is None:
            self.__appending_fns = {}
        else:
            self.__appending_fns = appending_fns

    def register_mapping_fn(self, layer_name: str, fn: Any):
        self.__mapping_fns[layer_name] = fn

    def register_appending_fn(self, layer_name: str, fn: Any):
        self.__appending_fns[layer_name] = fn

    def unregister_mapping_fn(self, layer_name: str):
        self.__mapping_fns[layer_name] = None

    def unregister_appending_fn(self, layer_name: str):
        self.__appending_fns[layer_name] = None

    # Generates panda df from the UIMA CAS: tokens, annotations, relations, uima (combined)
    def get_dataframes(self, cas):
        annotations = pd.DataFrame(columns=Annotation.COLS)
        relations = pd.DataFrame(columns=Relation.COLS)

        for element in cas.getAnnotationIndex():
            layer = element.FStype.name

            if element.FStype.name == 'uima.cas.Sofa':
                cas_text = '"' + html.unescape(element.sofaString) + '"'
                continue

            if len(element.getFeatures()) >= 1:
                row = {}
                for feature_dict in element.getFeatureValsAsDictList():
                    for feature_name, feature_value in feature_dict.items():
                        if feature_name == uima.BEGIN:
                            row[Annotation.BEGIN] = int(feature_value)
                        elif feature_name == uima.END:
                            row[Annotation.END] = int(feature_value)

                        if type(feature_value) is list:
                            if len(feature_value) > 1:
                                # TODO handle multiple values per UIMA feature
                                logging.warning(feature_value)
                                continue
                            feature_value = feature_value[0]

                            if layer in self.__mapping_fns:
                                row = self.__mapping_fns[layer](row, feature_name, feature_value)

                row[Annotation.ID] = int(element.FSid)
                row[Annotation.LAYER] = layer
                if layer in Layer.TOKEN:
                    row[Annotation.FEATURE_VAL] = cas_text[row[Annotation.BEGIN]+1:row[Annotation.END]+1]

                # add the layer to the data frame
                if layer in self.__appending_fns:
                    annotations, relations = self.__appending_fns[layer](row, annotations, relations)
                else:
                    warnings.warn("appending function not implemented for layer: " + layer)

        tokens = annotations[
            (annotations[Annotation.LAYER] == Layer.TOKEN) & (annotations[Annotation.FEATURE] == Token.TEXT)
        ][[Annotation.ID, Annotation.BEGIN, Annotation.END, Annotation.FEATURE_VAL]]
        tokens.reset_index(inplace=True, drop=True)
        tokens.rename(columns={Annotation.FEATURE_VAL: Token.TEXT}, inplace=True)

        pos_annotations = annotations[
            (annotations[Annotation.LAYER] == Layer.POS) & (annotations[Annotation.FEATURE] == Token.POS_VALUE)
        ][[Annotation.BEGIN, Annotation.END, Annotation.FEATURE_VAL]]  # TODO ID could be added if needed
        pos_annotations.rename(columns={Annotation.FEATURE_VAL: Token.POS_VALUE}, inplace=True)

        tokens = pd.merge(tokens, pos_annotations, on=[Annotation.BEGIN, Annotation.END], how='left')

        sentence_annotations = annotations[
            annotations[Annotation.LAYER] == Layer.SENTENCE
            ][[Annotation.BEGIN]]  # TODO ID could be added if needed
        sentence_annotations.loc[:, Token.SENT_START] = True
        tokens = pd.merge(tokens, sentence_annotations, on=[Annotation.BEGIN], how='left')

        dependency_annotations = relations[
            (relations[Relation.LAYER] == Layer.DEPENDENCY) & (relations[Relation.FEATURE] == Token.DEP_TYPE)
        ][[Relation.BEGIN, Relation.END, Relation.FEATURE_VAL, Token.GOV_ID]]
        dependency_annotations.rename(columns={Annotation.FEATURE_VAL: Token.DEP_TYPE}, inplace=True)
        tokens = pd.merge(tokens, dependency_annotations, on=[Relation.BEGIN, Relation.END], how='left')
        tokens = tokens.replace({pd.np.nan: None})

        # sets ID column as index
        annotations.set_index(Annotation.ID, inplace=True)
        relations.set_index(Relation.ID, inplace=True)

        return tokens, annotations, relations
