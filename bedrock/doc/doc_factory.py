from bedrock.doc.doc import Doc
from pycas.cas.core.CasFactory import CasFactory
from bedrock.common.cas2df import CAS2DataFrameConverter
from typing import Any
from bedrock.common.cas_converter_fns import CASConverterFns
import bedrock.common.utils as utils
import os


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





