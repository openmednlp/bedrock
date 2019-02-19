from bedrock.doc.doc import Doc
from typing import List
from bedrock.tagger.tagger_if import Tagger
from bedrock.prelabel.labeler_if import Labeler


class PreprocessingEngine:

    def __init__(self, tagger: Tagger, labelers: List[Labeler]):
        self.tagger = tagger
        self.labelers = labelers

    def __set_tags(self, docs: List[Doc]):
        for doc in docs:
            tokens, annotations, relations = self.tagger.get_tags(doc)
            doc.set_tokens(tokens)
            doc.set_annotations(annotations)
            doc.set_relations(relations)

    def __set_labels(self, docs: List[Doc]):
        for doc in docs:
            for labeler in self.labelers:
                doc.append_annotions(labeler.get_labels(doc))

    def preprocess(self, docs: List[Doc]) -> List[Doc]:
        self.__set_tags(docs)
        self.__set_labels(docs)
        return docs
