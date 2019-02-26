import unittest
import os
from bedrock.doc.docfactory import DocFactory
from bedrock.prelabel.regex_annotator import RegexAnnotator
from bedrock.prelabel.dictionary_labeler import DictionaryAnnotator
from bedrock.tagger.spacy_tagger import SpacyTagger
from bedrock.doc.doc import Layer
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
            with open(input_dir_path + file_names[i], 'r') as f:
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
        # dict_labeler = DictionaryLabeler(dictionary) TODO does not work

        preprocessing_engine = PreprocessingEngine(spacy_tagger, [regex_annotator]) #, dict_labeler])
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
