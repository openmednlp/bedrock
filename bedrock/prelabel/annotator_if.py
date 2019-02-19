from abc import ABC, abstractmethod
from bedrock.doc.doc_if import Doc
import pandas as pd


class Annotator(ABC):

    @abstractmethod
    def get_annotations(self, doc: Doc) -> (pd.DataFrame, pd.DataFrame):
        pass


