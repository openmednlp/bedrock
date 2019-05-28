from bedrock.doc.token import Token
from bedrock.doc.layer import Layer
from bedrock.doc.relation import Relation
from bedrock.doc.annotation import Annotation
from bedrock.common import uima


class CASConverterFns:
    @staticmethod
    def __token_2_df(row, feature_name, feature_value):
        if feature_name == uima.PosFeatureNames.POS_VALUE:
            row[Annotation.FEATURE] = Token.POS_VALUE
            row[Annotation.FEATURE_VAL] = feature_value
        return row

    @staticmethod
    def __pos_2_df(row, feature_name, feature_value):
        if feature_name == uima.PosFeatureNames.POS_VALUE:
            row[Annotation.FEATURE] = Token.POS_VALUE
            row[Annotation.FEATURE_VAL] = feature_value
        return row

    @staticmethod
    def __dependency_2_df(row, feature_name, feature_value):
        if feature_name == uima.DependencyFeatureNames.DEPENDENT:
            row[Relation.DEP_ID] = int(feature_value.FSid)
        elif feature_name == uima.DependencyFeatureNames.GOVERNOR:
            row[Relation.GOV_ID] = int(feature_value.FSid)
        elif feature_name == uima.DependencyFeatureNames.DEPENDENCY_TYPE:
            row[Relation.FEATURE] = Token.DEP_TYPE
            row[Relation.FEATURE_VAL] = feature_value
        return row

    @staticmethod
    def __token_appending(row, annotations, relations):
        row[Annotation.FEATURE] = Token.TEXT
        annotations = annotations.append(row, ignore_index=True)
        return annotations, relations

    @staticmethod
    def __sentence_appending(row, annotations, relations):
        row[Annotation.FEATURE] = None
        row[Annotation.FEATURE_VAL] = None
        annotations = annotations.append(row, ignore_index=True)
        return annotations, relations

    @staticmethod
    def __pos_appending(row, annotations, relations):
        annotations = annotations.append(row, ignore_index=True)
        return annotations, relations

    @staticmethod
    def __dependency_appending(row, annotations, relations):
        relations = relations.append(row, ignore_index=True)
        return annotations, relations

    @staticmethod
    def __token_2_cas(cas, layer, index, annotation):
        annotation = cas.createAnnotation(uima.StandardTypeNames.TOKEN, {
            uima.ID: index,
            uima.BEGIN: int(annotation[Annotation.BEGIN]),
            uima.END: int(annotation[Annotation.END])
        })
        return annotation

    @staticmethod
    def __pos_2_cas(cas, layer, index, annotation):
        annotation = cas.createAnnotation(uima.StandardTypeNames.POS, {
            uima.ID: index,
            uima.BEGIN: int(annotation[Annotation.BEGIN]),
            uima.END: int(annotation[Annotation.END]),
            uima.PosFeatureNames.POS_VALUE: annotation[Annotation.FEATURE_VAL]
        })
        return annotation

    @staticmethod
    def __sentence_2_cas(cas, layer, index, annotation):
        annotation = cas.createAnnotation(uima.StandardTypeNames.SENTENCE, {
            uima.ID: index,
            uima.BEGIN: int(annotation[Annotation.BEGIN]),
            uima.END: int(annotation[Annotation.END])
        })
        return annotation

    @staticmethod
    def __dependency_2_cas(cas, layer, index, relation):
        dependency = cas.createAnnotation(uima.StandardTypeNames.DEPENDENCY, {
            uima.ID: index,
            uima.BEGIN: int(relation[Relation.BEGIN]),
            uima.END: int(relation[Relation.END]),
            uima.DependencyFeatureNames.DEPENDENCY_TYPE: relation[Relation.FEATURE_VAL]
        })
        return dependency

    @staticmethod
    def get_mapping_functions() -> dict:
        return {
            Layer.TOKEN: CASConverterFns.__token_2_df,
            Layer.POS: CASConverterFns.__pos_2_df,
            Layer.DEPENDENCY: CASConverterFns.__dependency_2_df
        }

    @staticmethod
    def get_appending_functions() -> dict:
        return {
            Layer.TOKEN: CASConverterFns.__token_appending,
            Layer.SENTENCE: CASConverterFns.__sentence_appending,
            Layer.POS: CASConverterFns.__pos_appending,
            Layer.DEPENDENCY: CASConverterFns.__dependency_appending
        }

    @staticmethod
    def get_2_cas_functions() -> dict:
        return {
            Layer.TOKEN: CASConverterFns.__token_2_cas,
            Layer.POS: CASConverterFns.__pos_2_cas,
            Layer.SENTENCE: CASConverterFns.__sentence_2_cas,
            Layer.DEPENDENCY: CASConverterFns.__dependency_2_cas
        }
