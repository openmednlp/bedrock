'''
Created on Dez, 2018

@author: RA
'''
import os
import sys
import pandas as pd
import pandasql as pdsql
import numpy as np

##pysqldf maybe faster

from xml.sax.saxutils import quoteattr

from bedrock.pycas.cas.core.FeatureStructure import FeatureStructure
from bedrock.pycas.type.cas.TypeDescription import TypeDescription

class CAStoDf(object):
    '''
    This class writes a CAS object into csv format (including annotations)
    '''
    def __init__(self):
        '''
        Constructor
        Todo: add meta info to text, source, unique identifier etc
        '''
        # #name space qualifier of the root XMI element
        # self.__tagQualifier = 'xmi'
        # #name of the root XMI element
        # self.__tagName = 'XMI'
        # #version of the root XMI element
        # self.__version = '2.0'
        # #dictionary of XML name space, used to populate the name spaces in root XMI element
        # self.__xmlnsDict = {}
        # #list of name spaces
        # self.__xmlnsDictList = []
        # #this inner variable is used to add a number at the end of the name space if two name space is same
        # #usually name space is created from the second last domain qualifier of a type, if more than one type has
        # #same second last domain qualifier, but if the qualifiers up to the second last domain qualifier does not match
        # #then they are considered as different types and must have given a unique name space
        # #if the second last domain qualifier and qualifiers up to the second last domain qualifier matches then it considered
        # #under same name space
        # self.__TagQualifierCounter=1


    def writeToCSV(self, cas):
           return self.__toCSV(cas)


    def write(self,cas,filepath):
        try:
            if not (os.path.dirname(filepath) == ""):
                os.makedirs(os.path.dirname(filepath), exist_ok=True)

            uima_df, token_csv, anno_df, relation_df= self.__toDf(cas)
            token_csv.to_csv(filepath)
        except:
            print('Something went wrong! cannot create file',os.path.basename(filepath),'in',os.path.dirname(filepath))
            sys.exit(1)


    def toDf(self,cas):
        '''
        Generates panda df from the UIMA CAS: tokens, annotations, relations, uima (combined)
        '''

        uima_df = pd.DataFrame()
        anno_df = pd.DataFrame()
        relation_df = pd.DataFrame()
        token_df = pd.DataFrame()
        other_df = pd.DataFrame()

        xmi_id = 'nan'
        feature_type = ''
        begin = 'nan'
        end = 'nan'
        dep_anno_id = ''
        gov_anno_id = ''
        layer = ''
        #feature = ''
        class_name = ''
        cas_text = ''

        for element in cas.getAnnotationIndex():
            xmi_id = int(element.FSid)
            feature_type = element.FStype.name

            domlist = element.FStype.name.split('.')
            tagName = domlist[len(domlist) - 1]
            feature_type = tagName

            if (element.FStype.name == 'uima.cas.Sofa'):
                cas_text = escape(element.sofaString)

            if (len(element.getFeatures()) >= 1):
                for fdict in element.getFeatureValsAsDictList():
                    for fname, fval in fdict.items():
                        # get the sofa feature
                        if (fname == 'sofa'):
                            sofa = escape(fval.FSid)
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
                                        feature_type = 'Anno'
                                        class_name = fname
                                        feature_name = listval

                                fname_val = escape(listval)

                                if fname == 'Governor':
                                    gov_anno_id = escape(listval)
                                    layer = feature_type
                                    feature_type = "Relation"
                                if fname == 'Dependent':
                                    dep_anno_id = escape(listval)
                                    layer = feature_type
                                    feature_type = 'Relation'
                        else:
                            #TODO change add some meaningful stuff
                            feature_type='None'

            #add info to df
            if feature_type in ['Token','Sentence']:
                token_df=token_df.append({'feature_type':feature_type, 'xmi_id': xmi_id,
                                                'begin': begin, 'end': end}, ignore_index=True)

            elif feature_type == 'Anno':
                anno_df= anno_df.append({'feature_type':feature_type, 'xmi_id':xmi_id,
                                               'begin': begin, 'end': end, 'layer': layer, 'class_name': class_name,
                                               'feature_name': feature_name},  ignore_index=True)
            elif feature_type == 'Relation':
                rel_df.append({'feature_type': feature_type, 'xmi_id': xmi_id,
                                              'begin': begin, 'end':end, 'layer': layer,
                                              'gov_anno_id': gov_anno_id, 'dep_anno_id': dep_anno_id},  ignore_index=True)
            else:
                other_df.append({'feature_type':feature_type, 'xmi_id':xmi_id,
                                                 'begin':begin, 'end':end},  ignore_index=True)


        sentence_df = token_df[token_df['feature_type'] == 'Sentence']
        sentence_df['sent_id'] = sentence_df['xmi_id'].astype('category').cat.codes

        #output token list with added info annotation
        uima_df = token_df[token_df['feature_type'] == 'Token']
        uima_df['sent_id'] = 'nan'
        uima_df['token_id'] = range(0, len(uima_df))
        uima_df['text'] = ''
        #uima_df['begin'] = uima_df['begin'].astype('int')
        #uima_df['end'] = uima_df['end'].astype('int')
        uima_df.set_index('token_id')

        #add text, sent_id to uima_df, add token id to anno list
        anno_token_list = []
        for i in range(0,len(uima_df)):
            uima_df['text'].iloc[i] = cas_text[int(uima_df['begin'].iloc[i]+1):int(uima_df['end'].iloc[i]+1)]

            sent_lower_bd = sentence_df['begin'] <= uima_df['begin'].iloc[i]
            sent_upper_bd = sentence_df['end'] >= uima_df['begin'].iloc[i]
            sent_assign = np.multiply(sent_lower_bd,sent_upper_bd )

            if sum(sent_assign) > 0:
                uima_df['sent_id'].iloc[i] = sentence_df['sent_id'][sent_assign].iloc[0]
            else:
                uima_df['sent_id'].iloc[i] = 'nan'

            #add token id to anno
            if len(anno_df) > 0:
                token_anno = anno_df[(uima_df['begin'].iloc[i] >= anno_df['begin']) &
                                   (uima_df['begin'].iloc[i] <= anno_df['end'])]

                token_anno['token_id'] = uima_df['token_id'].iloc[i]
                anno_token_list.append(token_anno)



        #add annotations
        if len(anno_token_list) > 0:
            anno_token_df = pd.concat(anno_token_list)
            anno_token_df['col_pivot'] = anno_token_df['layer'] + "." + anno_token_df['class_name']
            t1 = anno_token_df.pivot(index ='token_id', values='feature_name',
                                        columns='col_pivot')
            uima_df = uima_df.merge(t1, left_on='token_id', right_index=True, how='left')

        #TODO add relations info to uima_df
        #maybe token_df not necessary as output

        return uima_df, token_df, anno_df, relation_df


    def __getTagQualifier(self, giventype):
        """ This method returns the tag qualifier for a given type
        """
        domain = giventype[0:giventype.rfind(".")]
        for nselem in self.__xmlnsDictList:
            if nselem['namespace'] == domain:
                tagQualifier = nselem['tagQualifier']
        return tagQualifier


def escape(s):
    return quoteattr(str(s))