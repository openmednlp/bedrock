from abc import ABC, abstractmethod
from bedrock.doc.doc import Doc


class Annotator(ABC):

    @abstractmethod
    def get_annotations(self, doc: Doc):
        pass


