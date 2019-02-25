import pandas as pd
import html
from pycas.cas.core import FeatureStructure
from pycas.type.cas.TypeDescription import TypeDescription
import pandasql as ps
from bedrock.doc.doc import Annotation, Token, Relation
from bedrock.common import uima


class CAS2DataFrameConverter:

    def get_dataframes(cas):

        '''
        Generates panda df from the UIMA CAS: tokens, annotations, relations, uima (combined)
        '''
        tokens = pd.DataFrame(columns=Token.COLS.value)
        annotations = pd.DataFrame(columns=Annotation.COLS.value)
        relations = pd.DataFrame(columns=Relation.COLS.value)

        for type in (uima.StandardTypeNames):
            print(type)

        for element in cas.getAnnotationIndex():
            xmi_id = int(element.FSid)
            feature_type = element.FStype.name

            domlist = element.FStype.name.split('.')
            tagName = domlist[len(domlist) - 1]
            feature_type = tagName

            if (element.FStype.name == 'uima.cas.Sofa'):
                cas_text = '"'+ html.unescape(element.sofaString) + '"'

            if (len(element.getFeatures()) >= 1):
                for fdict in element.getFeatureValsAsDictList():
                    for fname, fval in fdict.items():
                        # get the sofa feature
                        if (fname == 'sofa'):
                            sofa = fval.FSid
                        # get the begin
                        elif (fname == 'begin'):
                            begin = int(fval)
                        # get the end
                        elif (fname == 'end'):
                            end = int(fval)

                        # for all other features
                        elif type(fval) is list:
                                listval = ''
                                # iterate the list
                                for valelement in fval:
                                    # if its FS take fs id and add the FS to the fsNotInIndexListCheck
                                    if not (isinstance(valelement, TypeDescription) and isinstance(fval,FeatureStructure)):
                                        if(listval == ''):
                                            listval = str(valelement)
                                        else:
                                            listval + ' ' + str(valelement)
                                        layer = feature_type
                                        #feature_type = 'Anno'
                                        class_name = fname
                                        feature_name = listval

                                fname_val = listval

                                if fname == 'Governor':
                                    gov_anno_id = listval
                                    layer = feature_type
                                    #feature_type = "Relation"
                                if fname == 'Dependent':
                                    dep_anno_id = listval
                                    layer = feature_type
                                    #feature_type = 'Relation'
                        else:
                            #TODO change add some meaningful stuff
                            feature_type='None'

            #add info to df
            if feature_type in ['Token','Sentence']:
                tokens = tokens.append({'feature_type': feature_type, 'sofa_id': xmi_id,
                                                'begin': begin, 'end': end}, ignore_index=True)

            elif feature_type in ['POS', 'Tumor']:
                annotations= annotations.append({'feature_type': feature_type, 'sofa_id': xmi_id,
                                               'begin': begin, 'end': end, 'layer': layer, 'class_name': class_name,
                                               'feature_name': feature_name}, ignore_index=True)
            elif feature_type in ['Dependency', 'TumorRelation']:
                relations.append({'feature_type': feature_type, 'sofa_id': xmi_id,
                                              'begin': begin, 'end': end, 'layer': layer,
                                              'gov_anno_id': gov_anno_id, 'dep_anno_id': dep_anno_id},  ignore_index=True)
            else:
                other_df.append({'feature_type': feature_type, 'sofa_id':xmi_id,
                                                 'begin': begin, 'end':end}, ignore_index=True)


        sentence_df = tokens[tokens['feature_type'] == 'Sentence']
        sentence_df.loc[:,'sent_id'] = sentence_df['sofa_id'].astype('category').cat.codes

        #output token list with added info annotation
        uima_df = tokens[tokens['feature_type'] == 'Token']
        uima_df.loc[:,'token_id'] = range(0, len(uima_df))
        uima_df.loc[:,'text'] = ''
        uima_df.set_index('token_id')


        sqlsentid = '''
            select uima.*, sent.sent_id
            from uima_df uima
            left join sentence_df sent
            on uima.begin >= sent.begin
            and uima.begin <= sent.end 
            '''

        uima_df = ps.sqldf(sqlsentid, locals())

        # TODO check bounderies in join, left join??
        if annotations.empty == False:
            sqlanno = '''
                    select anno.class_name, anno.layer, 
                    uima.token_id,
                    group_concat(feature_name) feature_name
                    from annotations anno
                    inner join uima_df uima
                    on anno.begin <= uima.begin
                    and anno.end > uima.begin
                    group by token_id, class_name, layer 
                    '''
            anno_token_df = ps.sqldf(sqlanno, locals())
            anno_token_df.loc[:, 'col_pivot'] = anno_token_df['layer'] + "." + anno_token_df['class_name']

            t1 = anno_token_df.pivot(index='token_id', values='feature_name',
                                     columns='col_pivot')
            uima_df = uima_df.merge(t1, left_on = 'token_id', right_index = True, how='left')

        # add text to token list
        for i, row in uima_df.iterrows():
            uima_df.loc[i, 'text'] = cas_text[int(uima_df['begin'].iloc[i] + 1):int(uima_df['end'].iloc[i] + 1)]

        # TODO add dependency info to uima_df, maybe tokens not necessary as output
        return uima_df, tokens, annotations, relations

