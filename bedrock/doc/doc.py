import pandas as pd
from pycas.type.cas import TypeSystemFactory
from pycas.cas.core import CAS
from pycas.cas.writer import XmiWriter
from bedrock.common import uima, utils
from enum import Enum


class Token(Enum):
    ID = 'id'
    TEXT = 'text'
    BEGIN = 'begin'
    END = 'end'
    SENT_START = 'is_sent_start'
    POS_VALUE = 'pos_value'
    DEP_TYPE = 'dependency_type'
    GOV_ID = 'governor_id'
    ENTITY = 'entity'

    COLS = [ID, BEGIN, END, TEXT, SENT_START, POS_VALUE, DEP_TYPE, GOV_ID, ENTITY]

    def __str__(self):
        return str(self.value)


class Annotation(Enum):
    ID = 'id'
    BEGIN = 'begin'
    END = 'end'
    LAYER = 'layer'
    FEATURE = 'feature'
    FEATURE_VAL = 'feature_value'

    COLS = [ID, BEGIN, END, LAYER, FEATURE, FEATURE_VAL]

    def __str__(self):
        return str(self.value)


class Relation(Enum):
    ID = 'id'
    BEGIN = 'begin'
    END = 'end'
    LAYER = 'layer'
    FEATURE = 'feature'
    FEATURE_VAL = 'feature_value'
    GOV_ID = 'governor_id'
    DEP_ID = 'dependent_id'

    COLS = [ID, BEGIN, END, LAYER, FEATURE, FEATURE_VAL, GOV_ID, DEP_ID]

    def __str__(self):
        return str(self.value)


class Layer(Enum):
    TOKEN = utils.get_layer_name(uima.StandardTypeNames.TOKEN)
    POS = utils.get_layer_name(uima.StandardTypeNames.POS)
    SENT = utils.get_layer_name(uima.StandardTypeNames.SENTENCE)
    DEP = utils.get_layer_name(uima.StandardTypeNames.DEPENDENCY)
    TUMOR = utils.get_layer_name(uima.CustomTypeNames.TUMOR)


class Doc:

    def __init__(self):
        # TODO add uid, report_type, date, patient_number
        # TODO improvment by passing filename and text to constructor
        self.__text = ""
        self.__filename = ""
        self.__tokens = pd.DataFrame(columns=Token.COLS.value)
        self.__annotations = pd.DataFrame(columns=Annotation.COLS.value)
        self.__relations = pd.DataFrame(columns=Relation.COLS.value)

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

        if self.__tokens.empty:
            raise ValueError('token df empty in Doc.get_cas()')

        type_system_factory = TypeSystemFactory.TypeSystemFactory()
        type_system = type_system_factory.readTypeSystem(typesystem_filepath)
        cas = CAS.CAS(type_system)
        cas.documentText = self.get_text()
        cas.sofaMimeType = 'text'

        # iterate over annotations
        for _, annotation in self.__annotations.iterrows():

            layer = annotation[Annotation.LAYER]

            if layer == Layer.TOKEN:
                fs_anno = cas.createAnnotation(uima.StandardTypeNames.TOKEN, {
                    uima.BEGIN: int(annotation[Annotation.BEGIN]),
                    uima.END: int(annotation[Annotation.END])
                })
            elif layer == Layer.POS:
                fs_anno = cas.createAnnotation(uima.StandardTypeNames.POS, {
                    uima.BEGIN: int(annotation[Annotation.BEGIN]),
                    uima.END: int(annotation[Annotation.END]),
                    uima.PosFeatureNames.POS_VALUE: annotation[Annotation.FEATURE_VAL]
                })
            elif layer.startswith('custom'):  # TODO unclear
                fs_anno = cas.createAnnotation(uima.CustomTypeNames.TUMOR, {
                    uima.BEGIN: int(annotation[Annotation.BEGIN]),
                    uima.END: int(annotation[Annotation.END]),
                    annotation[Annotation.FEATURE]: annotation[Annotation.FEATURE_VAL]
                })
            elif layer == Layer.SENT:
                fs_anno = cas.createAnnotation(uima.StandardTypeNames.SENTENCE, {
                    uima.BEGIN: int(annotation[Annotation.BEGIN]),
                    uima.END: int(annotation[Annotation.END])
                })
            else:
                print(str(annotation) + ' unknown annotation')

            if fs_anno is not None:
                cas.addToIndex(fs_anno)

        for _, relation in self.__relations.iterrows():

            if relation[Relation.LAYER] == Annotation:
                fs_anno = cas.createAnnotation(uima.StandardTypeNames.DEPENDENCY, {
                    'begin': int(relation[Relation.BEGIN]),
                    'end': int(relation[Relation.END]),
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

    def write_xmi(self, file_name, typesystem_filepath):
        cas = self.get_cas(typesystem_filepath)
        xmi_writer = XmiWriter.XmiWriter()
        xmi_writer.write(cas, file_name)

    def load_pickle(file_path):
        return utils.load_pickle(file_path)
