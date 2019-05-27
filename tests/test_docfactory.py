import unittest
import os
from bedrock.doc.doc_factory import DocFactory
from dotenv import load_dotenv
from typing import Any
from doc.relation import Relation
from doc.annotation import Annotation
from doc.token import Token
from bedrock.common import uima
from pandas import DataFrame

load_dotenv()

TUMOR = 'webanno.custom.Tumor'
TUMOR_REL = 'webanno.custom.TumorRelation'


# TumorRelation
def tumor_relation_layer_mapping(row: dict, feature_name: str, feature_value: Any):
    if feature_name == uima.DependencyFeatureNames.DEPENDENT:
        row[Relation.DEP_ID] = int(feature_value.FSid)
    elif feature_name == uima.DependencyFeatureNames.GOVERNOR:
        row[Relation.GOV_ID] = int(feature_value.FSid)
    elif feature_name == uima.DependencyFeatureNames.DEPENDENCY_TYPE:
        row[Relation.FEATURE] = Token.DEP_TYPE
        row[Relation.FEATURE_VAL] = feature_value
    return row


# Tumor
def tumor_layer_mapping(row: dict, feature_name: str, feature_value: Any) -> dict:
    row[Annotation.FEATURE] = feature_name
    row[Annotation.FEATURE_VAL] = feature_value
    return row


# appending function for tumor
def tumor_layer_appending(row: dict, annotations: DataFrame, relations: DataFrame) -> (DataFrame, DataFrame):
    annotations = annotations.append(row, ignore_index=True)
    return annotations, relations


# adding fns for tumor relations
def tumor_relation_layer_appending(row: dict, annotations: DataFrame, relations: DataFrame) -> (DataFrame, DataFrame):
    relations = relations.append(row, ignore_index=True)
    return annotations, relations


class TestDocFactory(unittest.TestCase):

    def test_docfactory_from_xmi(self):
        input_dir_path = os.getenv("DATA_INPUT_PATH")
        output_dir_path = os.getenv("DATA_OUTPUT_PATH")
        typesystem_filepath = input_dir_path + "typesystem.xml"

        docfactory = DocFactory()
        docfactory.register_mapping_fn(TUMOR_REL, tumor_relation_layer_mapping)
        docfactory.register_mapping_fn(TUMOR, tumor_layer_mapping)
        docfactory.register_appending_fn(TUMOR, tumor_layer_appending)
        docfactory.register_appending_fn(TUMOR_REL, tumor_relation_layer_appending)

        file_names = [f for f in os.listdir(output_dir_path) if f.endswith('.xmi')]

        with open(typesystem_filepath, 'r') as f:
            typesystem_file_content = f.read()

        docs = list()
        for i in range(0, len(file_names)):
            with open(output_dir_path + file_names[i], 'r') as f:
                file_content = f.read()
                doc = docfactory.create_doc_from_xmi(file_content, typesystem_file_content, file_names[i])
                docs.append(doc)

        for idx, doc in enumerate(docs):
            relative_filepath_split = file_names[idx].split('/')
            filename = relative_filepath_split[len(relative_filepath_split)-1].split('.')
            doc.write_xmi(''.join([output_dir_path, filename[0], '_from_', filename[1], '.xmi']), typesystem_filepath)

        # TODO fix bug if tokens already in annotations when reading from UIMA XMI


if __name__ == '__main__':
    unittest.main()
