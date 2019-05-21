from bedrock.doc.doc import Doc, Token, Annotation, Relation
from bedrock.doc.relation import Relation
from typing import List
from bedrock.tagger.tagger import Tagger
from bedrock.prelabel.annotator import Annotator
import pandas as pd

class PreprocessingEngine:

    ID_OFFSET = 19

    def __init__(self, tagger: Tagger = None, annotators: List[Annotator] = None,
                 postlabeling_annotators: List[Annotator] = None):
        self.tagger = tagger
        self.annotators = annotators
        self.postlabeling_annotators = postlabeling_annotators

    def __set_tags(self, docs: List[Doc]):
        if self.tagger is not None:
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
        if self.annotators is not None:
            for doc in docs:
                for annotator in self.annotators:
                    annotations, relations = annotator.get_annotations(doc)
                    next_index = doc.get_next_start_index()  # returns 0 if doc.__annotations empty
                    if not annotations.empty:
                        annotations.index += next_index
                        max_annotations_index = annotations.index[-1]
                        doc.append_annotations(annotations, False)
                        if not relations.empty:  # relations cannot exist without annotations
                            relations[[Relation.GOV_ID, Relation.DEP_ID]] += next_index
                            relations.index += max_annotations_index+1
                            doc.append_relations(relations, False)

    def __run_postlabeling(self, docs: List[Doc]):
        if self.postlabeling_annotators is not None:
            for doc in docs:
                for post_annotator in self.postlabeling_annotators:
                    annotations, relations = post_annotator.get_annotations(doc)
                    doc.set_annotations(annotations)
                    if relations is not None:
                        doc.set_relations(relations)

    def preprocess(self, docs: List[Doc]) -> List[Doc]:
        self.__set_tags(docs)
        self.__set_annotations(docs)
        self.__run_postlabeling(docs)
        return docs
