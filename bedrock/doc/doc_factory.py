from bedrock.doc.doc import Doc
from bedrock.doc.token import Token
from bedrock.doc.annotation import Annotation
from bedrock.doc.relation import Relation
from pycas.cas.core.CasFactory import CasFactory
from bedrock.common.cas2df import CAS2DataFrameConverter
from typing import Any
from bedrock.common.cas_converter_fns import CASConverterFns
import bedrock.common.utils as utils
import os
import pandas as pd
import numpy as np


class DocFactory:

    def __init__(self):
        self.__cas_converter = CAS2DataFrameConverter(CASConverterFns.get_mapping_functions(),
                                                      CASConverterFns.get_appending_functions())
        self.__cas_converter_fns = {}


    def register_mapping_fn(self, layer_name: str, function: Any):
        self.__cas_converter.register_mapping_fn(layer_name, function)

    def register_appending_fn(self, layer_name: str, function: Any):
        self.__cas_converter.register_appending_fn(layer_name, function)

    def unregister_appending_fn(self, layer_name: str):
        self.__cas_converter.unregister_appending_fn(layer_name)

    def unregister_mapping_fn(self, layer_name: str):
        self.__cas_converter.unregister_mapping_fn(layer_name)

    def register_2_cas_fn(self, layer_name: str, function: Any):
        self.__cas_converter_fns[layer_name] = function

    def unregister_2_cas_fn(self, layer_name: str):
        self.__cas_converter_fns[layer_name] = None

    def create_doc_from_text(self, text: str, filename: str=None) -> Doc:
        doc = Doc()
        for layer_name in self.__cas_converter_fns:
            doc.register_converter_function(layer_name, self.__cas_converter_fns[layer_name])
        if filename is not None:
            doc.set_filename(filename)
        doc.set_text(utils.preprocess_text(text))
        return doc

    def create_doc_from_xmi(self, xmi_content: str, type_content: str, xmi_filename: str=None) -> Doc:
        doc = Doc()
        for layer_name in self.__cas_converter_fns:
            doc.register_converter_function(layer_name, self.__cas_converter_fns[layer_name])
        if xmi_filename is not None:
            doc.set_filename(xmi_filename)
        cas = CasFactory().buildCASfromStrings(xmi_content, type_content)
        tokens, annotations, relations = self.__cas_converter.get_dataframes(cas)
        doc.set_text(cas.documentText)
        doc.set_tokens(tokens)
        doc.set_annotations(annotations)
        doc.set_relations(relations)
        return doc

    def create_doc_from_dataframes(self, text: str, tokens: pd.DataFrame, annotations: pd.DataFrame,
                                   relations: pd.DataFrame) -> Doc:
        doc = Doc()
        doc_tokens = pd.DataFrame(columns=Token.COLS)
        doc_annotations = pd.DataFrame(columns=Annotation.COLS)
        doc_relations = pd.DataFrame(columns=Relation.COLS)

        index_mapping = dict()

        for _, row in tokens.iterrows():
            doc_tokens = doc_tokens.append({
                Token.ID: row[Token.ID],
                Token.BEGIN: row[Token.BEGIN],
                Token.END: row[Token.END],
                Token.POS_VALUE: row[Token.POS_VALUE],
                Token.SENT_START: row[Token.SENT_START],
                Token.DEP_TYPE: row[Token.DEP_TYPE],
                Token.GOV_ID: row[Token.GOV_ID]
            }, ignore_index=True)

        for _, row in annotations.iterrows():
            doc_annotations = doc_annotations.append({
                Annotation.BEGIN: row[Annotation.BEGIN],
                Annotation.END: row[Annotation.END],
                Annotation.LAYER: row[Annotation.LAYER],
                Annotation.FEATURE: row[Annotation.FEATURE],
                Annotation.FEATURE_VAL: row[Annotation.FEATURE_VAL]
            }, ignore_index=True)
            current_max_index = max(list(doc_annotations.index.values))
            index_mapping[row[Annotation.ID]] = current_max_index

        for _, row in relations.iterrows():
            gov_id = row[Relation.GOV_ID]
            if gov_id in index_mapping:
                gov_id = index_mapping[gov_id]
            dep_id = row[Relation.DEP_ID]
            if dep_id in index_mapping:
                dep_id = index_mapping[dep_id]
            doc_relations = doc_relations.append({
                Relation.BEGIN: row[Relation.BEGIN],
                Relation.END: row[Relation.END],
                Relation.LAYER: row[Relation.LAYER],
                Relation.FEATURE: row[Relation.FEATURE],
                Relation.FEATURE_VAL: row[Relation.FEATURE_VAL],
                Relation.GOV_ID: gov_id,
                Relation.DEP_ID: dep_id
            }, ignore_index=True)

        doc.set_text(text)
        doc.set_tokens(doc_tokens)
        doc.set_annotations(doc_annotations)
        doc.set_relations(doc_relations)
        return doc

    def create_doc_from_xmi_path(self, xmi_path: str, type_path: str) -> Doc:
        doc = Doc()
        for layer_name in self.__cas_converter_fns:
            doc.register_converter_function(layer_name, self.__cas_converter_fns[layer_name])
        _, filename = os.path.split(xmi_path)
        doc.set_filename(filename)
        cas = CasFactory().buildCAS(xmi_path, type_path)
        tokens, annotations, relations = self.__cas_converter.get_dataframes(cas)
        doc.set_text(cas.documentText)
        doc.set_tokens(tokens)
        doc.set_annotations(annotations)
        doc.set_relations(relations)
        return doc





