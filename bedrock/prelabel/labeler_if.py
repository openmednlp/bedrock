from abc import ABC, abstractmethod
from bedrock.doc.doc import Doc

class Labeler(ABC):

    @abstractmethod
    def get_labels(self, doc: Doc):
        pass


