import pandas as pd
import pandasql as pdsql

from doc.annotation import Annotation
from doc.layer import Layer
from doc.relation import Relation
from doc.token import Token
from pycas.type.cas import TypeSystemFactory
from pycas.cas.core import CAS
from pycas.cas.writer import XmiWriter
from bedrock.common import uima, utils
from typing import List


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

        if self.__annotations.empty == False:

            anno = self.__annotations
            token = self.__tokens
            tmp_col_name = 'feature_value_con'

            sqlanno = ''.join(['select anno.layer, anno.' , Annotation.FEATURE , ', token.' , \
                         Token.ID , ',group_concat(' , Annotation.FEATURE_VAL, ') ' , tmp_col_name , ' ', \
                        'from anno anno inner join token token on anno.' , Annotation.BEGIN , \
                        ' < token.' , Token.END , ' and anno.' , Annotation.END , ' > token.' , Token.BEGIN , \
                        ' where anno.', Annotation.LAYER ,' NOT IN ("POS","Token", "Sentence") ' ,
                        ' group by token.' , Token.ID , ', ' , Annotation.LAYER , ', ' , Annotation.FEATURE])

            tmp_anno_token_df = pdsql.sqldf(sqlanno, locals())
            tmp_anno_token_df.loc[:, 'col_pivot'] = tmp_anno_token_df[Annotation.LAYER] + "." + \
                                                    tmp_anno_token_df[Annotation.FEATURE].fillna('')

            tmp_anno_token_piv_df = tmp_anno_token_df.pivot(index='id', values=tmp_col_name, columns='col_pivot')

            wideformat = token.merge(tmp_anno_token_piv_df, left_on='id', right_index=True, how='left')
            wideformat.insert(0, 'doc_id', self.get_filename())


        return wideformat

    def write_xmi(self, file_name, typesystem_filepath):
        cas = self.get_cas(typesystem_filepath)
        xmi_writer = XmiWriter.XmiWriter()
        xmi_writer.write(cas, file_name)

    def load_pickle(file_path):
        return utils.load_pickle(file_path)
