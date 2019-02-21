import pandas as pd
import html
from pycas.cas.core import FeatureStructure
from pycas.type.cas.TypeDescription import TypeDescription
import pandasql as ps


class CAS2DataFrameConverter:

    def get_dataframes(cas):

        # TODO do refactoring!!
        '''
        Generates panda df from the UIMA CAS: tokens, annotations, relations, uima (combined)
        '''

        uima_df = pd.DataFrame()
        anno_df = pd.DataFrame()
        relation_df = pd.DataFrame()
        token_df = pd.DataFrame()
        other_df = pd.DataFrame()

        sofa_id = 'nan'
        feature_type = ''
        begin = 'nan'
        end = 'nan'
        dep_anno_id = ''
        gov_anno_id = ''
        layer = ''
        class_name = ''
        cas_text = ''

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
                token_df = token_df.append({'feature_type': feature_type, 'sofa_id': xmi_id,
                                                'begin': begin, 'end': end}, ignore_index=True)

            elif feature_type in ['POS', 'Tumor']:
                anno_df= anno_df.append({'feature_type': feature_type, 'sofa_id': xmi_id,
                                               'begin': begin, 'end': end, 'layer': layer, 'class_name': class_name,
                                               'feature_name': feature_name}, ignore_index=True)
            elif feature_type in ['Dependency', 'TumorRelation']:
                relation_df.append({'feature_type': feature_type, 'sofa_id': xmi_id,
                                              'begin': begin, 'end': end, 'layer': layer,
                                              'gov_anno_id': gov_anno_id, 'dep_anno_id': dep_anno_id},  ignore_index=True)
            else:
                other_df.append({'feature_type': feature_type, 'sofa_id':xmi_id,
                                                 'begin': begin, 'end':end}, ignore_index=True)


        sentence_df = token_df[token_df['feature_type'] == 'Sentence']
        sentence_df.loc[:,'sent_id'] = sentence_df['sofa_id'].astype('category').cat.codes

        #output token list with added info annotation
        uima_df = token_df[token_df['feature_type'] == 'Token']
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
        if anno_df.empty == False:
            sqlanno = '''
                    select anno.class_name, anno.layer, 
                    uima.token_id,
                    group_concat(feature_name) feature_name
                    from anno_df anno
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

        # TODO add dependency info to uima_df, maybe token_df not necessary as output
        return uima_df, token_df, anno_df, relation_df

