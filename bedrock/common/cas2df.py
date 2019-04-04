import pandas as pd
import html
from doc.relation import Relation
from doc.annotation import Annotation
from doc.token import Token
from doc.layer import Layer
from bedrock.common import uima

class CAS2DataFrameConverter:

    # Generates panda df from the UIMA CAS: tokens, annotations, relations, uima (combined)
    def get_dataframes(cas):
        annotations = pd.DataFrame(columns=Annotation.COLS)
        relations = pd.DataFrame(columns=Relation.COLS)

        for element in cas.getAnnotationIndex():
            layer = element.FStype.name.split('.')[-1]

            if element.FStype.name == 'uima.cas.Sofa':
                cas_text = '"' + html.unescape(element.sofaString) + '"'
                continue

            if len(element.getFeatures()) >= 1:
                row = {}
                for fdict in element.getFeatureValsAsDictList():
                    for fname, fval in fdict.items():
                        if fname == uima.BEGIN:
                            row[Annotation.BEGIN] = int(fval)
                        elif fname == uima.END:
                            row[Annotation.END] = int(fval)
                        if type(fval) is list:
                            if len(fval) > 1:
                                # TODO handle multiple values per UIMA feature
                                raise ValueError('UIMA features with multiple values not handled')
                            fval = fval[0]
                        if layer == Layer.POS:  # TODO instead of if .. elif => iterate through layers
                            if fname == uima.PosFeatureNames.POS_VALUE:
                                row[Annotation.FEATURE] = Token.POS_VALUE
                                row[Annotation.FEATURE_VAL] = fval
                        elif layer == Layer.DEPENDENCY:
                            if fname == uima.DependencyFeatureNames.DEPENDENT:
                                row[Relation.DEP_ID] = int(fval.FSid)
                            elif fname == uima.DependencyFeatureNames.GOVERNOR:
                                row[Relation.GOV_ID] = int(fval.FSid)
                            elif fname == uima.DependencyFeatureNames.DEPENDENCY_TYPE:
                                row[Relation.FEATURE] = Token.DEP_TYPE
                                row[Relation.FEATURE_VAL] = fval
                        elif layer == Layer.TUMOR:
                            row[Annotation.FEATURE] = fname
                            row[Annotation.FEATURE_VAL] = fval

                row[Annotation.ID] = int(element.FSid)
                row[Annotation.LAYER] = layer
                if layer in Layer.TOKEN:  # TODO instead of if .. elif => iterate through layers
                    row[Annotation.FEATURE] = Token.TEXT
                    row[Annotation.FEATURE_VAL] = cas_text[row[Annotation.BEGIN]+1:row[Annotation.END]+1]
                    annotations = annotations.append(row, ignore_index=True)
                elif layer == Layer.SENTENCE:
                    row[Annotation.FEATURE] = None
                    row[Annotation.FEATURE_VAL] = None
                    annotations = annotations.append(row, ignore_index=True)
                elif layer == Layer.POS:
                    annotations = annotations.append(row, ignore_index=True)
                elif layer == Layer.DEPENDENCY:
                    relations = relations.append(row, ignore_index=True)
                elif layer == Layer.TUMOR:
                    annotations = annotations.append(row, ignore_index=True)
                elif layer in [Layer.TUMOR_RELATION]:
                    raise ValueError('Layer '+layer+' not yet implemented')

        tokens = annotations[
            (annotations[Annotation.LAYER] == Layer.TOKEN) & (annotations[Annotation.FEATURE] == Token.TEXT)
        ][[Annotation.ID, Annotation.BEGIN, Annotation.END, Annotation.FEATURE_VAL]]
        tokens.reset_index(inplace=True, drop=True)
        tokens.rename(columns={Annotation.FEATURE_VAL: Token.TEXT}, inplace=True)

        pos_annotations = annotations[
            (annotations[Annotation.LAYER] == Layer.POS) & (annotations[Annotation.FEATURE] == Token.POS_VALUE)
        ][[Annotation.BEGIN, Annotation.END, Annotation.FEATURE_VAL]]  # TODO ID could be added if needed
        pos_annotations.rename(columns={Annotation.FEATURE_VAL: Token.POS_VALUE}, inplace=True)

        tokens = pd.merge(tokens, pos_annotations, on=[Annotation.BEGIN, Annotation.END], how='left')

        sentence_annotations = annotations[
            annotations[Annotation.LAYER] == Layer.SENTENCE
            ][[Annotation.BEGIN]]  # TODO ID could be added if needed
        sentence_annotations.loc[:, Token.SENT_START] = True
        tokens = pd.merge(tokens, sentence_annotations, on=[Annotation.BEGIN], how='left')

        dependency_annotations = relations[
            (relations[Relation.LAYER] == Layer.DEPENDENCY) & (relations[Relation.FEATURE] == Token.DEP_TYPE)
        ][[Relation.BEGIN, Relation.END, Relation.FEATURE_VAL, Token.GOV_ID]]
        dependency_annotations.rename(columns={Annotation.FEATURE_VAL: Token.DEP_TYPE}, inplace=True)
        tokens = pd.merge(tokens, dependency_annotations, on=[Relation.BEGIN, Relation.END], how='left')
        tokens = tokens.replace({pd.np.nan: None})

        return tokens, annotations, relations
