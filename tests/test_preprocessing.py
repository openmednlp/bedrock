import unittest
import os
from bedrock.doc.doc_factory import DocFactory
from bedrock.prelabel.regex_annotator import RegexAnnotator
from bedrock.tagger.spacy_tagger import SpacyTagger
from dotenv import load_dotenv
from pandas import DataFrame
from bedrock.engine import PreprocessingEngine
from typing import Any
from doc.relation import Relation
from doc.annotation import Annotation
from doc.token import Token
from bedrock.common import uima
import json

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


def tumor_convert_2_cas(cas, layer, index, annotation) -> Any:
    return cas.createAnnotation(layer, {
        uima.ID: index,
        uima.BEGIN: int(annotation[Annotation.BEGIN]),
        uima.END: int(annotation[Annotation.END]),
        annotation[Annotation.FEATURE]: annotation[Annotation.FEATURE_VAL]
    })


def tumor_relation_convert_2_cas(cas, layer, index, relation) -> Any:
    return  cas.createAnnotation(layer, {
        uima.ID: index,
        uima.BEGIN: int(relation[Relation.BEGIN]),
        uima.END: int(relation[Relation.END])
    })

class TestPreprocessing:

    def test_preprocessing_from_text(self):
        input_dir_path = os.getenv("DATA_INPUT_PATH")
        output_dir_path = os.getenv("DATA_OUTPUT_PATH")
        typesystem_filepath = input_dir_path + "typesystem.xml"

        docfactory = DocFactory()
        docfactory.register_mapping_fn(TUMOR_REL, tumor_relation_layer_mapping)
        docfactory.register_mapping_fn(TUMOR, tumor_layer_mapping)
        docfactory.register_appending_fn(TUMOR, tumor_layer_appending)
        docfactory.register_appending_fn(TUMOR_REL, tumor_relation_layer_appending)
        docfactory.register_2_cas_fn(TUMOR, tumor_convert_2_cas)
        docfactory.register_2_cas_fn(TUMOR_REL, tumor_relation_convert_2_cas)

        with open(typesystem_filepath, 'r') as f:
            typesystem_file_content = f.read()

        txt_filenames = []
        xmi_filenames = []
        txt_docs = []
        xmi_docs = []
        for filename in os.listdir(input_dir_path):
            if filename.endswith('.txt'):
                with open(input_dir_path + filename, 'r') as f:
                    txt_filenames.append(filename)
                    file_text = f.read()
                    doc = docfactory.create_doc_from_text(file_text, filename)
                    txt_docs.append(doc)
            elif filename.endswith('.xmi'):
                with open(input_dir_path + filename, 'r') as f:
                    xmi_filenames.append(filename)
                    file_content = f.read()
                    doc = docfactory.create_doc_from_xmi(file_content, typesystem_file_content, filename)
                    xmi_docs.append(doc)

        spacy_tagger = SpacyTagger("de_core_news_sm")

        # initialize regex labeler
        with open(os.getenv("TNM_PATTERNS"), 'r') as f:
            tnm_regex_patterns = json.loads(f.read())

        regex_annotator = RegexAnnotator(tnm_regex_patterns, TUMOR)

        # initialize dictionary labeler
        # dictionary = pd.read_csv(os.getenv("ICD_O_FILE_PATH"), sep='\t')
        # dictionary = dictionary[dictionary['languageCode'] == 'de']
        # dictionary = dictionary.drop(columns=['effectiveTime', 'languageCode', 'Source'])
        # dict_annotator = DictionaryTreeAnnotator('fuzzy-dictionary-tree-labeler', dictionary['term'].tolist(),
        #                                          dictionary['Group'].tolist(),
        #                                          dictionary['referencedComponentId'].tolist())

        # load the dictionary from a pickle file
        # dict_annotator = DictionaryTreeAnnotator('fuzzy-dictionary-tree-labeler',
        #                                         saved_tree_path=os.getenv('DICTIONARY_PATH'))

        # save the dictionary
        # dict_annotator.save_dictionary(os.getenv('DICTIONARY_PATH'))

        # # initialize post processing annotator
        # with open(os.getenv("POST_LABELING_RULES"), 'r') as f:
        #     post_labeling_rules = json.loads(f.read())
        # postlabeling_annotator = PostlabelingAnnotator(post_labeling_rules)


        # build preprocessing engine and start it
        preprocessing_engine = PreprocessingEngine(spacy_tagger, [regex_annotator], None)
                                                   # [postlabeling_annotator])
        preprocessing_engine.preprocess(txt_docs)

        for idx, doc in enumerate(txt_docs):
            filename = txt_filenames[idx].split('.')
            # print(doc.get_wideformat())
            doc.write_xmi(''.join([output_dir_path, filename[0], '_from_', filename[1], '.xmi']), typesystem_filepath)

        for idx, doc in enumerate(xmi_docs):
            filename = xmi_filenames[idx].split('.')
            # doc.write_xmi(''.join([output_dir_path, filename[0], '_from_', filename[1], '.xmi']), typesystem_filepath)

        preprocessing_engine = PreprocessingEngine(annotators=[regex_annotator])
        preprocessing_engine.preprocess(xmi_docs)

        for idx, doc in enumerate(xmi_docs):
            filename = xmi_filenames[idx].split('.')
            doc.write_xmi(''.join([output_dir_path, filename[0], '_from_', filename[1], '_tnmregex' , '.xmi']), typesystem_filepath)


if __name__ == '__main__':
    TestPreprocessing().test_preprocessing_from_text()
