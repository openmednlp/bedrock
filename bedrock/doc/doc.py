import pandas as pd
from bedrock.pycas.type.cas import TypeSystemFactory
from bedrock.pycas.cas.core import CAS
from bedrock.pycas.cas.writer import XmiWriter
from bedrock.utils import uima


class Doc:

    def __init__(self):

        # TODO add uid, report_type, date, patient_number
        # TODO improvment by passing filename and text to constructor

        self._text = ""
        self._filename = ""

        columns = ['begin', 'end', 'layer', 'feature', 'feature_value']
        self._annotations = pd.DataFrame(columns=columns)

        columns = ['id', 'text', 'begin', 'end', 'is_sent_start', 'pos_value', 'dependency_type', 'governor_id', 'entity']
        self._tokens = pd.DataFrame(columns=columns)

        columns = ['begin', 'end', 'governor_id', 'layer', 'feature', 'feature_value', 'dependent_id']
        self._relations = pd.DataFrame(columns=columns)

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

    def remove_annotation(self, sofa_id_list):
        rm = self._annotations['sofa_id'].isin(sofa_id_list)
        if sum(rm) > 0:
           self._annotations = self._annotations[rm == False]

    def remove_relation(self, sofa_id_list):
        rm = self._relations['sofa_id'].isin(sofa_id_list)
        if sum(rm) > 0:
           self._relations = self._relations[rm == False]

    def save_as_pickle(self, file_path):
        import bedrock.common
        bedrock.common.save_pickle(self, file_path)

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

            # get the layer of the annotation
            layer = annotation['layer']

            # add an token annotation
            if layer == 'token':
                fs_anno = cas.createAnnotation(uima.StandardTypeNames.TOKEN, {
                    'begin': int(annotation['begin']),
                    'end': int(annotation['end'])
                }, int(annotation['id']))
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
                print(relation['feature_value'])
                print(type(relation['feature_value']))
                fs_anno = cas.createAnnotation(uima.StandardTypeNames.DEPENDENCY, {
                    'begin': int(relation['begin']),
                    'end': int(relation['end']),
                    uima.DependencyFeatureNames.GOVERNOR: int(relation['governor_id']),
                    uima.DependencyFeatureNames.DEPENDENT: int(relation['dependent_id']),
                    uima.DependencyFeatureNames.DEPENDENCY_TYPE: relation['feature_value']
                })
                cas.addToIndex(fs_anno)


        # TODO add dependencies to cas
        # < dependency: Dependency
        # xmi: id = "6501"
        # sofa = "1"
        # begin = "60"
        # end = "63"
        # Governor = "78"
        # Dependent = "92"
        # DependencyType = "acl"
        # flavor = "basic" / >
        return cas

    def write_xmi(self, file_name, typesystem_filepath):
        cas = self.get_cas(typesystem_filepath)
        xmi_writer = XmiWriter.XmiWriter()
        xmi_writer.write(cas, file_name)

    def load_pickle(file_path):
        import bedrock.common
        return bedrock.common.load_pickle(file_path)
