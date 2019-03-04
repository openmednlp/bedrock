import pandas as pd
import html
from pycas.cas.core import FeatureStructure, CAS
from pycas.type.cas.TypeDescription import TypeDescription
import pandasql as ps
from doc.relation import Relation
from doc.annotation import Annotation
from doc.token import Token
from doc.layer import Layer
from bedrock.common import uima
from bedrock.common import utils


class CAS2DataFrameConverter:

    # Generates panda df from the UIMA CAS: tokens, annotations, relations, uima (combined)
    def get_dataframes(cas):
        tokens = pd.DataFrame(columns=Token.COLS)
        annotations = pd.DataFrame(columns=Annotation.COLS)
        relations = pd.DataFrame(columns=Relation.COLS)
        ml_prepared = pd.DataFrame()

        for element in cas.getAnnotationIndex():
            layer = element.FStype.name.split('.')[-1]

            if element.FStype.name == 'uima.cas.Sofa':
                cas_text = '"' + html.unescape(element.sofaString) + '"'

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
                        if layer == Layer.POS:
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
                if layer in Layer.TOKEN:
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
                # elif layer in [Layer.TUMOR_RELATION]:

        # sentence_df = tokens[tokens['feature_type'] == 'Sentence']
        # sentence_df.loc[:, 'sent_id'] = sentence_df['sofa_id'].astype('category').cat.codes
        #
        # # output token list with added info annotation
        # ml_prepared = tokens[tokens['feature_type'] == 'Token']
        # ml_prepared.loc[:, 'token_id'] = range(0, len(ml_prepared))
        # ml_prepared.loc[:, 'text'] = ''
        # ml_prepared.set_index('token_id')
        #
        # sqlsentid = '''
        #     select uima.*, sent.sent_id
        #     from ml_prepared uima
        #     left join sentence_df sent
        #     on uima.begin >= sent.begin
        #     and uima.begin <= sent.end
        #     '''
        #
        # ml_prepared = ps.sqldf(sqlsentid, locals())
        #
        # # TODO check bounderies in join, left join??
        # if annotations.empty == False:
        #     sqlanno = '''
        #             select anno.class_name, anno.layer,
        #             uima.token_id,
        #             group_concat(feature_name) feature_name
        #             from annotations anno
        #             inner join ml_prepared uima
        #             on anno.begin < uima.end
        #             and anno.end > uima.begin
        #             group by token_id, class_name, layer
        #             '''
        #     anno_token_df = ps.sqldf(sqlanno, locals())
        #     anno_token_df.loc[:, 'col_pivot'] = anno_token_df['layer'] + "." + anno_token_df['class_name']
        #
        #     t1 = anno_token_df.pivot(index='token_id', values='feature_name',
        #                              columns='col_pivot')
        #     ml_prepared = ml_prepared.merge(t1, left_on='token_id', right_index=True, how='left')
        #
        # # add text to token list
        # for i, row in ml_prepared.iterrows():
        #     ml_prepared.loc[i, 'text'] = cas_text[int(ml_prepared['begin'].iloc[i] + 1):int(ml_prepared['end'].iloc[i] + 1)]

        # TODO add dependency info to ml_prepared, maybe tokens not necessary as output
        return ml_prepared, tokens, annotations, relations
