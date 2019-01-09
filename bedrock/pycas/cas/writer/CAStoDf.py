'''
Created on Dez, 2018

@author: RA
'''
import os
import sys
import pandas as pd
import pandasql as pdsql

##pysqldf maybe faster

from xml.sax.saxutils import quoteattr

from pycas.cas.core.FeatureStructure import FeatureStructure
from pycas.type.cas.TypeDescription import TypeDescription

class CAStoDf(object):
    '''
    This class writes a CAS object into csv format (including annotations)
    '''
    def __init__(self):
        '''
        Constructor
        To do: add meta info to text, source, unique identifier etc
        '''
        #name space qualifier of the root XMI element
        self.__tagQualifier = 'xmi'
        #name of the root XMI element
        self.__tagName = 'XMI'
        #version of the root XMI element
        self.__version = '2.0'
        #dictionary of XML name space, used to populate the name spaces in root XMI element
        self.__xmlnsDict = {}
        #list of name spaces
        self.__xmlnsDictList = []
        #this inner variable is used to add a number at the end of the name space if two name space is same
        #usually name space is created from the second last domain qualifier of a type, if more than one type has
        #same second last domain qualifier, but if the qualifiers up to the second last domain qualifier does not match
        #then they are considered as different types and must have given a unique name space
        #if the second last domain qualifier and qualifiers up to the second last domain qualifier matches then it considered
        #under same name space
        self.__TagQualifierCounter=1

    "This method returns the CAS as a XMI String"
    def writeToCSV(self, cas):
           return self.__toCSV(cas)

    "This method writes the CAS as a csv file to the given path(file name also included in the path)"
    def write(self,cas,filepath):
        try:
            if not (os.path.dirname(filepath) == ""):
                os.makedirs(os.path.dirname(filepath), exist_ok=True)

            token_csv, cas_element_csv = self.__toCSV(cas)
            token_csv.to_csv(filepath)
        except:
            print('Something went wrong! cannot create file',os.path.basename(filepath),'in',os.path.dirname(filepath))
            sys.exit(1)

    def toDf(self,cas):
        "This internal method generates csv tables from the CAS object so that it can be written"

        cas_element_df = pd.DataFrame()
        dep_anno_id = ''
        gov_anno_id = ''
        fname_2 = ''
        #get the unique types from type system to build the name spaces
        nslist = []
        for typeName in cas.typesystem.getAllTypeDesc():
            if (not typeName.name in nslist):
                nslist.append(typeName.name)

        #holds the list of unique urls
        urlList = []
        # holds list of name space qualifier already generated
        tagList = []
        #iterate through unique types and build url and name space qualifier, add them if not added before to xmlnsDictList
        for ns in nslist:
            domainurl = 'http:///'+ns[0:ns.rfind(".")].replace('.','/')+'.ecore'
            Secondlastval=ns.split('.')[len(ns.split('.'))-2]
            tagQualifier=Secondlastval
            while True:
                #if domain url already exists do not add
                if domainurl in urlList:
                    break
                #if domain url doesnot exist add
                else:
                    #if the name space qualifier is already used add a number at the end to make it unique, otherwise add
                    if not tagQualifier in tagList:
                        self.__xmlnsDictList.append({'namespace': ns[0:ns.rfind(".")], 'tagQualifier': tagQualifier, 'domainurl': domainurl})
                        urlList.append(domainurl)
                        tagList.append(tagQualifier)
                        break
                    else:
                        self.__TagQualifierCounter = self.__TagQualifierCounter + 1
                        tagQualifier= Secondlastval+str(self.__TagQualifierCounter)



        fsNotInIndexListCheck= []
        indexedFsIdArray = []
        #get the list of annotations or FS in the CAS
        for element in cas.getAnnotationIndex():
            #add cas:null element
            if( element.FStype.name == 'uima.cas.NULL'):
                domlist=element.FStype.name.split('.')
                tagName=domlist[len(domlist)-1]
                tagQualifier=self.__getTagQualifier(element.FStype.name)
                #casnull='<'+tagQualifier+':'+tagName+' xmi:id='+escape(element.FSid)+'/>'
                #add the id to the indexedFsIdArray to record that this FS is already processed
                indexedFsIdArray.append(element.FSid)


            #add cas:sofa element (text
            if( element.FStype.name == 'uima.cas.Sofa'):
                domlist=element.FStype.name.split('.')
                tagName=domlist[len(domlist)-1]
                tagQualifier=self.__getTagQualifier(element.FStype.name)
                # cassofa='<'+tagQualifier+':'+tagName+' xmi:id='+escape(element.FSid)+' sofaNum='+escape(element.sofaNum)+' ' \
                #     'sofaID='+ escape(element.sofaID)+' mimeType='+ escape(element.mimeType)+ ' sofaString='+escape(element.sofaString)+'/>'

                cas_text = escape(element.sofaString)

                #add the id to the indexedFsIdArray to record that this FS is already processed
                indexedFsIdArray.append(int(element.FSid))

            #add other feature structures
            else:
                domlist=element.FStype.name.split('.')
                tagName=domlist[len(domlist)-1]
                tagQualifier=self.__getTagQualifier(element.FStype.name)  #type 4
                #casfs='<'+tagQualifier+':'+tagName+' xmi:id='+escape(element.FSid)+''
                casfs = escape(element.FSid)
                #add the id to the indexedFsIdArray to record that this FS is already processed
                indexedFsIdArray.append(element.FSid)

                fname_val=''
                sofa=''
                begin=''
                end=''


                #if the FS has features iterate through list of features and serialize
                if(len(element.getFeatures()) >= 1):
                    for fdict in element.getFeatureValsAsDictList():
                        for fname,fval in fdict.items():
                            #get the sofa feature
                            if(fname =='sofa'):
                                #sofa = ' sofa=' +escape(fval.FSid)+''
                                sofa = escape(fval.FSid)
                            #get the begin
                            elif(fname == 'begin'):
                                #begin = ' begin=' +escape(fval)+''
                                begin= escape(fval)
                            #get the end
                            elif(fname == 'end'):
                                #end = ' end=' +escape(fval)+''
                                end = escape(fval)

                            #for all other features
                            else:
                                #if feature value is not a list
                                if not type(fval) is list:
                                    #if its FS take FSid and add the FS to the fsNotInIndexListCheck
                                    if (isinstance(fval,TypeDescription) and isinstance(fval,FeatureStructure)):
                                        #fspoprs=fspoprs+' '+fname+'='+escape(fval.FSid)
                                        fsNotInIndexListCheck.append(fval)
                                    #else:
                                        #fspoprs=fspoprs+' '+fname+'='+escape(fval)
                                #if feature value is a list
                                elif type(fval) is list:
                                    listval=''
                                    #iterate the list
                                    for valelement in fval:
                                        #if its FS take fs id and add the FS to the fsNotInIndexListCheck
                                        if (isinstance(valelement,TypeDescription) and isinstance(valelement,FeatureStructure)):
                                            listval = str(valelement.FSid) if (listval == '') else listval+' '+str(valelement.FSid)
                                            fsNotInIndexListCheck.append(valelement)
                                        else:
                                            listval = str(valelement) if (listval == '') else listval+' '+str(valelement)
                                    #fspoprs=fspoprs+' '+ fname +'='+ escape(listval)+''
                                    fname_2 = fname
                                    fname_val = escape(listval)

                                    if fname == 'Governor':
                                        gov_anno_id = escape(listval)
                                        fname_2 = "relation"
                                    if fname == 'Dependent':
                                        dep_anno_id = escape(listval)
                                        fname_2 = 'relation'
                                    if (fname_2 == 'name' or fname_2 == 'isLastSegment' ):
                                        fname_2 = ''
                                else:
                                    raise TypeError('type of feature',fname,'not recognized')

                # add attributes to csv files
                cas_element_df = cas_element_df.append({'type': tagName, 'tagQualifier': tagQualifier, 'xmid': casfs,
                                            'doc_id': sofa, 'begin': begin, 'end': end,
                                            'fname': fname_2, 'fname_val': fname_val, 'dep_anno_id': dep_anno_id,
                                            'gov_anno_id': gov_anno_id }, ignore_index=True)

        # prepare token list, convert to wide
        cas_element_df['begin'] = cas_element_df['begin'].str.replace("\"", "").astype(int)
        cas_element_df['end'] = cas_element_df['end'].str.replace("\"", "").astype(int)
        cas_element_df['xmid'] = cas_element_df['xmid'].str.replace("\"", "").astype(int)

        token_df = cas_element_df[cas_element_df['type'] == 'Token']
        token_df['text'] = ''

        # token_id consecutively numbered
        token_df['token_id'] = range(0, len(token_df))


        # add sentence id and token text to token_df
        token_df['sent_id'] = 'nan'
        sentence_df = cas_element_df[cas_element_df['type'] == 'Sentence']
        sentence_df['sent_id'] = sentence_df['xmid'].astype('category').cat.codes

        anno_list=[]
        anno_df = cas_element_df[(cas_element_df['tagQualifier'] == 'custom') &
                                 (cas_element_df['fname'] != 'relation')]
        anno_df.rename(columns={'xmid': 'anno_id', 'type': 'layer', 'fname': 'feature', 'fname_val' : 'class'},
                        inplace = True)


        #add text to token df, add token_id to anno_df
        for i in range(0,len(token_df)):
            token_df['text'].iloc[i] = cas_text[token_df['begin'].iloc[i]+1:token_df['end'].iloc[i]+1]
            token_df['sent_id'].iloc[i] = sentence_df['sent_id'][ ( sentence_df['begin'] <= token_df['begin'].iloc[i]) &
                            ( sentence_df['end'] >= token_df['begin'].iloc[i])].values[0]
            tmp_anno = anno_df[( token_df['begin'].iloc[i] >= anno_df['begin'] ) &
                                ( token_df['begin'].iloc[i] <= anno_df['end'] )]

            tmp_anno['token_id'] = token_df['token_id'].iloc[i]
            anno_list.append(tmp_anno)

        anno_df = pd.concat(anno_list)


        relation_df = cas_element_df[(cas_element_df['tagQualifier'] == 'custom') &
                            (cas_element_df['fname'] == 'relation')][['doc_id', 'gov_anno_id', 'dep_anno_id','type']]
        relation_df['role'] = None
        relation_df.rename(columns={'type': 'layer'}, inplace = True)


        return token_df[['doc_id', 'sent_id', 'token_id', 'begin', 'end', 'text']], \
               anno_df[['doc_id', 'anno_id', 'token_id', 'begin', 'end', 'layer', 'feature', 'class']], \
               relation_df[['doc_id', 'gov_anno_id', 'dep_anno_id', 'layer', 'role']]



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