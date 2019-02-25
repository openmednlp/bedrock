from bedrock.doc.doc import Doc
from typing import List
from bedrock.tagger.tagger_if import Tagger
from bedrock.prelabel.annotator_if import Annotator


class PreprocessingEngine:

    def __init__(self, tagger: Tagger, annotators: List[Annotator]):
        self.tagger = tagger
        self.annotators = annotators

    def __set_tags(self, docs: List[Doc]):
        for doc in docs:
            tokens, annotations, relations = self.tagger.get_tags(doc)
            doc.set_tokens(tokens)
            doc.set_annotations(annotations)
            doc.set_relations(relations)
            # print("Tokens:")
            # print(tokens)
            # print("\n")
            # print("Annotations:")
            # print(annotations)
            # print("\n")
            # print("Relations:")
            # print(relations)
            # print("\n")

    def __set_annotations(self, docs: List[Doc]):
        for doc in docs:
            for annotator in self.annotators:
                annotations, relations = annotator.get_annotations(doc)
                doc.append_annotions(annotations)
                doc.append_relations(relations)

    def preprocess(self, docs: List[Doc]) -> List[Doc]:
        self.__set_tags(docs)
        self.__set_annotations(docs)
        return docs
