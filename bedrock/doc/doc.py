import pandas as pd

from doc.annotation import Annotation
from doc.layer import Layer
from doc.relation import Relation
from doc.token import Token
from pycas.type.cas import TypeSystemFactory
from pycas.cas.core import CAS
from pycas.cas.writer import XmiWriter
from bedrock.common import uima, utils

class Doc:

    def __init__(self):
        # TODO add uid, report_type, date, patient_number
        # TODO improvment by passing filename and text to constructor
        self.__text = ""
        self.__filename = ""
        self.__tokens = pd.DataFrame(columns=Token.COLS)
        self.__annotations = pd.DataFrame(columns=Annotation.COLS)
        self.__relations = pd.DataFrame(columns=Relation.COLS)

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

    def append_annotions(self, annotations: pd.DataFrame):
        self.__annotations = self.__annotations.append(annotations)

    def set_tokens(self, tokens: pd.DataFrame):
        self.__tokens = tokens

    def get_tokens(self) -> pd.DataFrame:
        return self.__tokens

    def set_relations(self, relations: pd.DataFrame):
        self.__relations = relations

    def get_relations(self) -> pd.DataFrame:
        return self.__relations

    def append_relations(self, relations: pd.DataFrame):
        self.__relations = self.__relations.append(relations)

    def save_as_pickle(self, file_path):
        utils.save_pickle(self, file_path)

    def get_cas(self, typesystem_filepath):
        type_system_factory = TypeSystemFactory.TypeSystemFactory()
        type_system = type_system_factory.readTypeSystem(typesystem_filepath)
        cas = CAS.CAS(type_system)
        cas.documentText = self.get_text()
        cas.sofaMimeType = 'text'

        # iterate over annotations
        for _, annotation in self.__annotations.iterrows():

            layer = annotation[Annotation.LAYER]
            fs_anno = None

            if layer == Layer.TOKEN:
                fs_anno = cas.createAnnotation(uima.StandardTypeNames.TOKEN, {
                    uima.ID: int(annotation[Annotation.ID]),
                    uima.BEGIN: int(annotation[Annotation.BEGIN]),
                    uima.END: int(annotation[Annotation.END])
                })
            elif layer == Layer.POS:
                fs_anno = cas.createAnnotation(uima.StandardTypeNames.POS, {
                    uima.BEGIN: int(annotation[Annotation.BEGIN]),
                    uima.END: int(annotation[Annotation.END]),
                    uima.PosFeatureNames.POS_VALUE: annotation[Annotation.FEATURE_VAL]
                })
            elif layer == Layer.TUMOR:  # TODO unclear
                fs_anno = cas.createAnnotation(uima.CustomTypeNames.TUMOR, {
                    uima.BEGIN: int(annotation[Annotation.BEGIN]),
                    uima.END: int(annotation[Annotation.END]),
                    annotation[Annotation.FEATURE]: annotation[Annotation.FEATURE_VAL]
                })
            elif layer == Layer.SENTENCE:
                fs_anno = cas.createAnnotation(uima.StandardTypeNames.SENTENCE, {
                    uima.BEGIN: int(annotation[Annotation.BEGIN]),
                    uima.END: int(annotation[Annotation.END])
                })
            else:
                print(str(annotation) + ' unknown annotation')

            if fs_anno is not None:
                cas.addToIndex(fs_anno)

        for _, relation in self.__relations.iterrows():

            if relation[Relation.LAYER] == Layer.DEPENDENCY:
                fs_anno = cas.createAnnotation(uima.StandardTypeNames.DEPENDENCY, {
                    uima.BEGIN: int(relation[Relation.BEGIN]),
                    uima.END: int(relation[Relation.END]),
                    uima.DependencyFeatureNames.DEPENDENCY_TYPE: relation[Relation.FEATURE_VAL]
                })
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

                # TODO add flavor feature ? "flavor":"basic"
        return cas

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
            sentence_label = 'Sencente'

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
                .apply(lambda y: ','.join(list(map(lambda x: str(x), list(y[Annotation.FEATURE_VAL]))))) \
                .reset_index(name=Annotation.FEATURE_VAL)

            tmp_annotations_token_df.loc[:, pivot_name] = tmp_annotations_token_df[Annotation.LAYER] + "." + \
                                                          tmp_annotations_token_df[Annotation.FEATURE].fillna('')

            tmp_annotations_token_df = tmp_annotations_token_df.pivot(index=Token.ID, values=Annotation.FEATURE_VAL,
                                                                      columns=pivot_name)

            wide_format = self.get_tokens().merge(tmp_annotations_token_df, left_on=Token.ID, right_index=True,
                                                  how='left')
            wide_format.insert(0, doc_id_name, self.get_filename())

            return wide_format

        return None

    def write_xmi(self, file_name, typesystem_filepath):
        cas = self.get_cas(typesystem_filepath)
        xmi_writer = XmiWriter.XmiWriter()
        xmi_writer.write(cas, file_name)

    def load_pickle(file_path):
        return utils.load_pickle(file_path)
