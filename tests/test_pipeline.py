import unittest
from bedrock.pipeline import Pipeline
import bedrock.common.utils as utils
from bedrock.prelabel.dictionary_tree_annotator import DictionaryTreeAnnotator
from bedrock.doc.annotation import Annotation
from bedrock.prelabel.postlabeling_annotator import PostlabelingAnnotator
import json


class TestPipeline(unittest.TestCase):

    def test_parse_text(self):
        with open('tests/data/input/TNM_1.txt', 'r') as f:
            file_text = f.read()
        docs = Pipeline(language='de_core_news_sm').parse_text(file_text).get_docs()
        self.assertEqual(len(docs), 1)
        doc = docs[0]
        self.assertEqual(doc.get_text(), utils.preprocess_text(file_text))

    def test_get_docs(self):
        with open('tests/data/input/TNM_1.txt', 'r') as f:
            file_text1 = f.read()
        with open('tests/data/input/TNM_2.txt', 'r') as f:
            file_text2 = f.read()
        docs = Pipeline(language='de_core_news_sm').parse_text(file_text1).parse_text(file_text2).get_docs()
        self.assertEqual(len(docs), 2)
        doc1 = docs[0]
        doc2 = docs[1]
        self.assertEqual(doc1.get_text(), utils.preprocess_text(file_text1))
        self.assertEqual(doc2.get_text(), utils.preprocess_text(file_text2))

    def test_parse_from_xmi(self):
        docs = Pipeline(language='de_core_news_sm').parse_cas('tests/data/input/TNM_1.xmi',
                                                              'tests/data/input/typesystem.xml').get_docs()

        doc = docs[0]
        self.assertEqual(len(doc.get_annotations().index), 185)
        self.assertEqual(len(doc.get_tokens().index), 177)

    def test_set_tags(self):
        with open('tests/data/input/TNM_1.txt', 'r') as f:
            file_text = f.read()
        pipeline = Pipeline(language='de_core_news_sm').parse_text(file_text)
        doc = pipeline.get_docs()[0]
        tokens = doc.get_tokens()
        annotations = doc.get_annotations()
        relations = doc.get_relations()
        print(len(tokens.index), len(annotations.index), len(relations.index))
        self.assertEqual(len(tokens.index), 0)
        self.assertEqual(len(annotations.index), 0)
        self.assertEqual(len(relations.index), 0)

        doc = pipeline.set_tags().get_docs()[0]
        tokens = doc.get_tokens()
        annotations = doc.get_annotations()
        relations = doc.get_relations()
        self.assertEqual(len(tokens.index), 169)
        self.assertEqual(len(annotations.index), 357)
        self.assertEqual(len(relations.index), 169)
        self.assertEqual(doc.get_text(), utils.preprocess_text(file_text))

    def test_set_annotations(self):
        with open('tests/data/input/TNM_1.txt', 'r') as f:
            file_text = f.read()
        pipeline = Pipeline(language='de_core_news_sm').parse_text(file_text).set_tags()
        pipeline.set_annotator(DictionaryTreeAnnotator('dictionary-tree-annotator', 'layer',
                                                       ['Plattenepithelkarzinom', 'Resektionsrand', 'Lymphknoten'],
                                                       ['what', 'where', 'where'], ['1', '2', '3']))
        docs = pipeline.set_annotations().get_docs()
        doc = docs[0]
        annotations = doc.get_annotations()
        annotations = annotations[annotations[Annotation.LAYER] == 'layer']
        self.assertEqual(len(annotations.index), 6)
        where = annotations[annotations[Annotation.FEATURE] == 'where']
        self.assertEqual(len(where.index), 4)
        what = annotations[annotations[Annotation.FEATURE] == 'what']
        self.assertEqual(len(what.index), 2)

    def test_run_postlabeling(self):
        with open('tests/data/input/TNM_1.txt', 'r') as f:
            file_text = f.read()
        pipeline = Pipeline(language='de_core_news_sm').parse_text(file_text).set_tags()
        pipeline.set_annotator(DictionaryTreeAnnotator('dictionary-tree-annotator', 'layer',
                                                       ['Plattenepithelkarzinom', 'Resektionsrand', 'Lymphknoten'],
                                                       ['what', 'where', 'where'], ['1', '2', '3']))
        post_labeling_rules = json.loads('[{\
            "window": 0, "ignore_sentence_boundaries": false,\
            "identifier": [{ "column": "feature", "value": "where" }],\
            "requires": [{ "column": "feature", "value": "test" }]\
        }]')
        pipeline.set_post_labeling_annotator(PostlabelingAnnotator(post_labeling_rules))
        docs = pipeline.set_annotations().run_post_labeling().get_docs()
        doc = docs[0]
        annotations = doc.get_annotations()
        annotations = annotations[annotations[Annotation.LAYER] == 'layer']
        self.assertEqual(len(annotations.index), 2)
        where = annotations[annotations[Annotation.FEATURE] == 'where']
        self.assertEqual(len(where.index), 0)
        what = annotations[annotations[Annotation.FEATURE] == 'what']
        self.assertEqual(len(what.index), 2)


if __name__ == '__main__':
    unittest.main()
