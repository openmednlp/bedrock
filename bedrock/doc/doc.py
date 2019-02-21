import pandas as pd
from pycas.type.cas import TypeSystemFactory
from pycas.cas.core import CAS
from pycas.cas.writer import XmiWriter
from common import uima


class Doc:

    def __init__(self):

        # TODO add uid, report_type, date, patient_number
        # TODO improvment by passing filename and text to constructor

        self._text = ""
        self._filename = ""

        # TODO define using:
        # columns = ['layer', 'feature', 'feature_value', 'origin']
        # self._annotations = pd.DataFrame(columns=columns)
        #
        # columns = ['sent_id', 'token_id', 'text', 'beg', 'end', 'is_sent_start', 'pos', 'dep', 'origin']
        # self._tokens = pd.DataFrame(columns=columns)
        #
        # columns = ['doc_id', 'sofa_id', 'gov_anno_id', 'dep_anno_id', 'layer', 'role', 'origin']
        # self._relations = pd.DataFrame(columns=columns)

    def set_text(self, text: str):
        self._text = text

    def get_text(self) -> str:
        return self._text

    def set_filename(self, filename: str):
        self._filename = filename

    def get_filename(self):
        return self._filename

    def set_annotations(self, annotations: pd.DataFrame):
        self._annotations = annotations

    def get_annotations(self) -> pd.DataFrame:
        return self._annotations

    def append_annotions(self, annotations: pd.DataFrame):
        self._annotations = self._annotations.append(annotations)

    def set_tokens(self, tokens: pd.DataFrame):
        self._tokens = tokens

    def get_tokens(self) -> pd.DataFrame:
        return self._tokens

    def set_relations(self, relations: pd.DataFrame):
        self._relations = relations

    def get_relations(self) -> pd.DataFrame:
        return self._relations

    def append_relations(self, relations: pd.DataFrame):
        self._relations = self._relations.append(relations)

    def save_as_pickle(self, file_path):
        common.utils.save_pickle(self, file_path)

    def get_cas(self, typesystem_filepath):

        if self._tokens.empty:
            raise ValueError('token df empty in Doc.get_cas()')

        type_system_factory = TypeSystemFactory.TypeSystemFactory()
        type_system = type_system_factory.readTypeSystem(typesystem_filepath)
        cas = CAS.CAS(type_system)
        cas.documentText = self.get_text()
        cas.sofaMimeType = 'text'

        # iterate over annotations
        for _, annotation in self._annotations.iterrows():

            layer = annotation['layer']

            if layer == 'token':
                fs_anno = cas.createAnnotation(uima.StandardTypeNames.TOKEN, {
                    'begin': int(annotation['begin']),
                    'end': int(annotation['end'])
                })
            elif layer == 'pos':
                fs_anno = cas.createAnnotation(uima.StandardTypeNames.POS, {
                    'begin': int(annotation['begin']),
                    'end': int(annotation['end']),
                    uima.PosFeatureNames.POS_VALUE: annotation['feature_value']
                })
            elif layer.startswith('custom'):  # TODO unclear
                fs_anno = cas.createAnnotation(uima.CustomTypeNames.TUMOR, {
                    'begin':  int(annotation['begin']),
                    'end': int(annotation['end']),
                    annotation['feature']: annotation['feature_value']
                })
            elif layer == 'sentence':
                fs_anno = cas.createAnnotation(uima.StandardTypeNames.SENTENCE, {
                    'begin': int(annotation['begin']),
                    'end': int(annotation['end'])
                })
            else:
                print(str(annotation) + ' unknown annotation')

            if fs_anno is not None:
                cas.addToIndex(fs_anno)

        for _, relation in self._relations.iterrows():

            if relation['layer'] == 'dependency':
                fs_anno = cas.createAnnotation(uima.StandardTypeNames.DEPENDENCY, {
                    'begin': int(relation['begin']),
                    'end': int(relation['end']),
                    uima.DependencyFeatureNames.DEPENDENCY_TYPE: relation['feature_value']
                })
                cas.addToIndex(fs_anno)

                fs_governor = None
                fs_dependent = None
                for fs in cas.getAnnotationIndex():
                    if fs.FSid == int(relation['governor_id']):
                        fs_governor = fs
                    if fs.FSid == int(relation['dependent_id']):
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
        return common.utils.load_pickle(file_path)
