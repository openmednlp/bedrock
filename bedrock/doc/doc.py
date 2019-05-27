import pandas as pd

from doc.annotation import Annotation
from doc.layer import Layer
from doc.relation import Relation
from doc.token import Token
from pycas.type.cas import TypeSystemFactory
from pycas.cas.core import CAS
from pycas.cas.writer import XmiWriter
from bedrock.common import uima, utils
import warnings
from typing import Any
from common.cas_converter_fns import CASConverterFns


class Doc:

    def __init__(self, text: str = "", filename: str = "", converter_2_df_functions=None):
        self.__text = text
        self.__filename = filename
        self.__tokens = pd.DataFrame(columns=Token.COLS)
        self.__annotations = pd.DataFrame(columns=Annotation.COLS)
        self.__relations = pd.DataFrame(columns=Relation.COLS)
        self._meta_data = {}

        if converter_2_df_functions is None:
            self.__converter_fns = CASConverterFns.get_2_cas_functions()
        else:
            self.__converter_fns = converter_2_df_functions

    def register_converter_function(self, layer_name: str, function: Any):
        self.__converter_fns[layer_name] = function

    def unregister_converter_function(self, layer_name: str):
        self.__converter_fns[layer_name] = None

    def set_text(self, text: str):
        self.__text = text

    def get_text(self) -> str:
        return self.__text

    def set_filename(self, filename: str):
        self.__filename = filename

    def get_filename(self):
        return self.__filename

    def set_annotations(self, annotations: pd.DataFrame):
        self.__annotations = annotations

    def get_annotations(self) -> pd.DataFrame:
        return self.__annotations

    def append_annotations(self, annotations: pd.DataFrame, ignore_index: bool):
        if annotations is not None:
            self.__annotations = self.__annotations.append(annotations, ignore_index=ignore_index)

    def set_tokens(self, tokens: pd.DataFrame):
        self.__tokens = tokens

    def get_tokens(self) -> pd.DataFrame:
        return self.__tokens

    def set_relations(self, relations: pd.DataFrame):
        self.__relations = relations

    def get_relations(self) -> pd.DataFrame:
        return self.__relations

    def append_relations(self, relations: pd.DataFrame, ignore_index: bool):
        if relations is not None:
            self.__relations = self.__relations.append(relations, ignore_index=ignore_index)

    def save_as_pickle(self, file_path):
        utils.save_pickle(self, file_path)

    def get_cas(self, typesystem_filepath):
        type_system_factory = TypeSystemFactory.TypeSystemFactory()
        type_system = type_system_factory.readTypeSystem(typesystem_filepath)
        cas = CAS.CAS(type_system)
        cas.documentText = self.get_text()
        cas.sofaMimeType = 'text'

        # iterate over annotations
        for index, annotation in self.__annotations.iterrows():

            layer = annotation[Annotation.LAYER]
            fs_anno = None

            if layer in self.__converter_fns:
                fs_anno = self.__converter_fns[layer](cas, layer, index, annotation)
            else:
                warnings.warn(str(annotation) + ' unknown annotation')

            if fs_anno is not None:
                cas.addToIndex(fs_anno)

        for index, relation in self.__relations.iterrows():

            layer = relation[Relation.LAYER]
            fs_anno = None

            if layer in self.__converter_fns:
                fs_anno = self.__converter_fns[layer](cas, layer, index, relation)

            else:
                raise ValueError('unknown relation layer')

            cas.addToIndex(fs_anno)

            fs_governor = None
            fs_dependent = None
            for fs in cas.getAnnotationIndex():
                if fs.FSid == int(relation[Relation.GOV_ID]):
                    fs_governor = fs
                if fs.FSid == int(relation[Relation.DEP_ID]):
                    fs_dependent = fs
            if fs_dependent is None:
                raise ValueError("cannot set dependent. dependet feature is None")
            setattr(fs_anno, uima.DependencyFeatureNames.DEPENDENT, fs_dependent)
            if fs_governor is None:
                raise ValueError("cannot set governor. governor feature is None")
            setattr(fs_anno, uima.DependencyFeatureNames.GOVERNOR, fs_governor)

        return cas

    def set_meta_data(self, key: str, value: str):
        self._meta_data[key] = value

    def get_meta_data(self, key: str) -> str:
        return self._meta_data[key]

    def has_meta_key(self, key: str) -> bool:
        if key in self._meta_data:
            return True
        return False

    def get_meta_data_frame(self):
        keys = list(self._meta_data.keys())
        values = list(self._meta_data.values())
        return pd.DataFrame({'key': keys, 'value': values})

    def get_wideformat(self):
        '''
              :ivar: tokens and annotations class members

              :Restrictions:
              Assumes that a token can have only one feature.value assigned from the same feature. In case of multiple
              annotations will be concatinated.
              An annotation is assigned to a token even it does not span the whole token, the wide format does not reflect
              partial annotations of a token.

              :return: table of tokens and their annotations in wide format
              '''

        if self.__annotations.empty is False:

            pivot_name = 'col_pivot'
            doc_id_name = 'doc_id'
            pos_label = 'POS'
            token_label = 'Token'
            sentence_label = 'Sentence'

            # save all annotations that belong to a token
            extended_annotations = pd.DataFrame()

            for index, token in self.get_tokens().iterrows():
                annotations = self.get_annotations()[(self.get_annotations()[Annotation.BEGIN] < token[Token.END]) &
                                                     (self.get_annotations()[Annotation.END] > token[Token.BEGIN]) &
                                                     (~self.get_annotations()[Annotation.LAYER].isin([pos_label,
                                                                                                      token_label,
                                                                                                      sentence_label]))]\
                    .copy()
                annotations[Token.ID] = token[Token.ID]
                extended_annotations = extended_annotations.append(annotations)

            tmp_annotations_token_df = extended_annotations.groupby([Token.ID, Annotation.LAYER, Annotation.FEATURE]) \
                .apply(lambda y: ','.join(list(map(lambda x: str(x), list(y[Annotation.FEATURE_VAL])))))\
                .reset_index().rename(columns={0: Annotation.FEATURE_VAL})

            if tmp_annotations_token_df.empty is False:
                tmp_annotations_token_df.loc[:, pivot_name] = tmp_annotations_token_df[Annotation.LAYER] + "." + \
                                                          tmp_annotations_token_df[Annotation.FEATURE].fillna('')
                tmp_annotations_token_df = tmp_annotations_token_df.pivot(index=Token.ID, values=Annotation.FEATURE_VAL,
                                                                      columns=pivot_name)

            wide_format = self.get_tokens().merge(tmp_annotations_token_df, left_on=Token.ID, right_index=True,
                                                  how='left')
            wide_format.insert(0, doc_id_name, self.get_filename())

            return wide_format

        return pd.DataFrame()

    def write_xmi(self, file_name, typesystem_filepath):
        cas = self.get_cas(typesystem_filepath)
        xmi_writer = XmiWriter.XmiWriter()
        xmi_writer.write(cas, file_name)

    def load_pickle(file_path):
        return utils.load_pickle(file_path)

    def get_next_start_index(self) -> int:
        if self.__annotations.empty:
            return 0

        max_annotations_index = max(self.__annotations.index)

        max_relations_index = -1 if self.__relations.empty else max(self.__relations.index)

        if max_annotations_index > max_relations_index:
            return max_annotations_index + 1

        return max_relations_index + 1
