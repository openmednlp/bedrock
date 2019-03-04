import unittest
import os
from bedrock.doc.docfactory import DocFactory
from bedrock.prelabel.regex_annotator import RegexAnnotator
from bedrock.prelabel.postlabeling_annotator import PostlabelingAnnotator
from bedrock.prelabel.dictionary_tree_annotator import DictionaryTreeAnnotator
from bedrock.tagger.spacy_tagger import SpacyTagger
from doc.layer import Layer
from dotenv import load_dotenv
import pandas as pd
import json
from bedrock.preprocessing import PreprocessingEngine

load_dotenv()


class TestPreprocessing(unittest.TestCase):

    def test_preprocessing_from_text(self):
        input_dir_path = os.getenv("DATA_INPUT_PATH")
        output_dir_path = os.getenv("DATA_OUTPUT_PATH")
        typesystem_filepath = input_dir_path + "typesystem.xml"

        file_names = [f for f in os.listdir(input_dir_path) if f.endswith('.txt')]

        docs = list()
        for i in range(0, len(file_names)):
            with open(input_dir_path + file_names[i], 'r', encoding='utf-8') as f:
                file_text = f.read()
                doc = DocFactory.create_doc_from_text(file_text, file_names[i])
                docs.append(doc)

        spacy_tagger = SpacyTagger(os.getenv("SPACY_MODEL_PATH"))

        # initialize regex labeler
        with open(os.getenv("TNM_PATTERNS"), 'r') as f:
            tnm_regex_patterns = json.loads(f.read())

        regex_annotator = RegexAnnotator(tnm_regex_patterns, Layer.TUMOR)

        # initialize dictionary labeler
        dictionary = pd.read_csv(os.getenv("ICD_O_FILE_PATH"), sep='\t')
        dictionary = dictionary[dictionary['languageCode'] == 'de']
        dictionary = dictionary.drop(columns=['effectiveTime', 'languageCode', 'Source'])

        dict_annotator = DictionaryTreeAnnotator(dictionary['term'].tolist(),
                                                 dictionary['Group'].tolist(),
                                                 dictionary['referencedComponentId'].tolist(),
                                                 'fuzzy-dictionary-tree-labeler')

        # initialize post processing annotator
        with open(os.getenv("POST_LABELING_RULES"), 'r') as f:
            post_labeling_rules = json.loads(f.read())
        postlabeling_annotator = PostlabelingAnnotator(post_labeling_rules)


        # build preprocessing engine and start it
        preprocessing_engine = PreprocessingEngine(spacy_tagger, [regex_annotator, dict_annotator], [postlabeling_annotator])
        preprocessing_engine.preprocess(docs)


        for idx, doc in enumerate(docs):
            relative_filepath_split = file_names[idx].split('/')
            filename = relative_filepath_split[len(relative_filepath_split)-1].split('.')
            doc.write_xmi(''.join([output_dir_path, filename[0], '_from_', filename[1], '.xmi']), typesystem_filepath)
            # #write to csv
            # uima_df, token_df, anno_df, rel_df = CAStoDf().toDf(utx.cas)
            # uima_df.to_csv(output_dir_path + file_names[file].replace('.xmi', '_uima.csv'), sep="\t", index=False)
            # anno_df.to_csv(output_dir_path + file_names[file].replace('xmi', '_anno.csv'), sep="\t", index=False)


if __name__ == '__main__':
    unittest.main()
