from abc import ABC, abstractmethod
from bedrock.doc.doc_if import Doc

class Labeler(ABC):

    @abstractmethod
    def get_labels(self, doc: Doc):
        pass


