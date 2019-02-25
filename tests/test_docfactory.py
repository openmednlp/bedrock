import unittest
import os
from bedrock.doc.docfactory import DocFactory
from dotenv import load_dotenv

load_dotenv()


class TestDocFactory(unittest.TestCase):

    def test_docfactory_from_xmi(self):
        input_dir_path = os.getenv("DATA_INPUT_PATH")
        output_dir_path = os.getenv("DATA_OUTPUT_PATH")
        typesystem_filepath = input_dir_path + "typesystem.xml"

        file_names = [f for f in os.listdir(input_dir_path) if f.endswith('.xmi')]

        with open(typesystem_filepath, 'r') as f:
            typesystem_file_content = f.read()

        docs = list()
        for i in range(0, len(file_names)):
            with open(input_dir_path + file_names[i], 'r') as f:
                file_content = f.read()
                doc = DocFactory.create_doc_from_xmi(file_content, typesystem_file_content, file_names[i])
                docs.append(doc)

        # for idx, doc in enumerate(docs):
        #     relative_filepath_split = file_names[idx].split('/')
        #     filename = relative_filepath_split[len(relative_filepath_split)-1].split('.')
        #     doc.write_xmi(''.join([output_dir_path, filename[0], '_from_', filename[1], '.xmi']), typesystem_filepath)


if __name__ == '__main__':
    unittest.main()
