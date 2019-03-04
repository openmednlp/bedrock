from abc import ABC, abstractmethod
from bedrock.doc.doc import Doc
import pandas as pd


class Tagger(ABC):

    @abstractmethod
    def get_tags(self, doc: Doc) -> (pd.DataFrame, pd.DataFrame, pd.DataFrame):
        pass




