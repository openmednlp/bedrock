import unittest
import os
from bedrock.doc.docfactory import DocFactory
from bedrock.prelabel.regex_annotator import RegexAnnotator
from bedrock.prelabel.postlabeling_annotator import PostlabelingAnnotator
from bedrock.prelabel.dictionary_tree_annotator import DictionaryTreeAnnotator
from bedrock.tagger.spacytagger import SpacyTagger
from doc.layer import Layer
from dotenv import load_dotenv
import pandas as pd
import json
from bedrock.preprocessing import PreprocessingEngine

load_dotenv()


class TestPreprocessing:

    def test_preprocessing_from_text(self):
        input_dir_path = os.getenv("DATA_INPUT_PATH")
        output_dir_path = os.getenv("DATA_OUTPUT_PATH")
        typesystem_filepath = input_dir_path + "typesystem.xml"

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
                    doc = DocFactory.create_doc_from_text(file_text, filename)
                    txt_docs.append(doc)
            elif filename.endswith('.xmi'):
                with open(input_dir_path + filename, 'r') as f:
                    xmi_filenames.append(filename)
                    file_content = f.read()
                    doc = DocFactory.create_doc_from_xmi(file_content, typesystem_file_content, filename)
                    xmi_docs.append(doc)

        spacy_tagger = SpacyTagger("de_core_news_sm")

        # initialize regex labeler
        with open(os.getenv("TNM_PATTERNS"), 'r') as f:
            tnm_regex_patterns = json.loads(f.read())

        regex_annotator = RegexAnnotator(tnm_regex_patterns, Layer.TUMOR)

        # initialize dictionary labeler
        dictionary = pd.read_csv(os.getenv("ICD_O_FILE_PATH"), sep='\t')
        dictionary = dictionary[dictionary['languageCode'] == 'de']
        dictionary = dictionary.drop(columns=['effectiveTime', 'languageCode', 'Source'])
        dict_annotator = DictionaryTreeAnnotator('fuzzy-dictionary-tree-labeler', Layer.TUMOR,
                                                 dictionary['term'].tolist(),
                                                 dictionary['Group'].tolist(),
                                                 dictionary['referencedComponentId'].tolist())

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
        preprocessing_engine = PreprocessingEngine(spacy_tagger, [regex_annotator, dict_annotator], None)
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
