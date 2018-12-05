'''
Created on Jan 23, 2017

@author: Dibyojyoti
'''
import os
import sys
import pandas as pd

from xml.sax.saxutils import quoteattr

from pycas.cas.core.FeatureStructure import FeatureStructure
from pycas.type.cas.TypeDescription import TypeDescription

class CSVWriter(object):
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
    "This internal method generates csv table from the CAS object so that it can be written"
    def __toCSV(self,cas):

        cas_element_csv = pd.DataFrame()
        dep_id=''
        gov_id=''

        #get the unique types from type system to build the name spaces
        nslist = []
        for typeName in cas.typesystem.getAllTypeDesc():
            if (not typeName.name in nslist):
                nslist.append(typeName.name)
        #build the name space dictionary, contains name space, name space qualifier and url
        #url is created from name space to be added in root element of XMI with the name space qualifier

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
        #add the name space for the XMI to xmlnsDictList
        #self.__xmlnsDictList.append({'namespace': 'www.omg.org', 'tagQualifier': 'xmi', 'domainurl': 'http://www.omg.org/XMI'})



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

                                    if fname=='Governor':
                                        gov_id=escape(listval)
                                        fname_2="relation"
                                    if fname=='Dependent':
                                        dep_id=escape(listval)
                                        fname_2='relation'
                                    if (fname_2 == 'name' or fname_2 == 'isLastSegment'):
                                        fname_2=''
                                else:
                                    raise TypeError('type of feature',fname,'not recognized')

                # add attributes to csv files
                cas_element_csv = cas_element_csv.append({'type':tagName, 'tagQualifier':tagQualifier, 'xmid': casfs,
                                            'doc_id': sofa, 'begin': begin, 'end':end,
                                            'fname':fname_2, 'fname_val':fname_val, 'dependent_id': dep_id, 'governor_id':gov_id },
                                            ignore_index=True)

                #add attributes with vale
                #casfs= casfs + sofa + begin + end + fspoprs


                #add closing
                #casfs = casfs+'/>'

                #xmistr = xmistr + casfs
        #Now check the FS added in fsNotInIndexListCheck if they are processed means in indexedFsIdArray ignore, otherwise process
        #this is done because all the referenced FS are not added in index of the CAS
        # for fs in fsNotInIndexListCheck:
        #     if( not fs.FSid in indexedFsIdArray):
        #         domlist=fs.FStype.name.split('.')
        #         tagName=domlist[len(domlist)-1]
        #         tagQualifier=self.__getTagQualifier(fs.FStype.name)
        #         casfs='<'+tagQualifier+':'+tagName+' xmi:id='+escape(fs.FSid)+''
        #
        #         fspoprs=''
        #         sofa=''
        #         begin=''
        #         end=''
        #         #if the FS has features iterate through list of features and serialize
        #         if(len(fs.getFeatures()) >= 1):
        #             for fdict in fs.getFeatureValsAsDictList():
        #                 for fname,fval in fdict.items():
        #                     if(fname =='sofa'):
        #                         sofa = ' sofa=' +escape(fval.FSid)+''
        #                     #get the begin
        #                     elif(fname == 'begin'):
        #                         begin = ' begin=' +escape(fval)+''
        #                     #get the end
        #                     elif(fname == 'end'):
        #                         end = ' end=' +escape(fval)+''
        #                     else:
        #                         if not type(fval) is list:
        #                             #if its FS take FSid
        #                             if (isinstance(fval,TypeDescription) and isinstance(fval,FeatureStructure)):
        #                                 fspoprs=fspoprs+' '+fname+'='+escape(fval.FSid)+''
        #                             else:
        #                                 fspoprs=fspoprs+' '+fname+'='+escape(fval)+''
        #                         elif type(fval) is list:
        #                             listval=''
        #                             for valelement in fval:
        #                                 #if its FS
        #                                 if (isinstance(valelement,TypeDescription) and isinstance(valelement,FeatureStructure)):
        #                                     listval = escape(valelement.FSid) if (listval == '') else listval+' '+escape(valelement.FSid)
        #                                 else:
        #                                     listval = escape(valelement) if (listval == '') else listval+' '+escape(valelement)
        #                             fspoprs=fspoprs+' '+fname+'='+listval+''
        #                         else:
        #                             raise TypeError('type of feature',fname,'not recognized')



        #prepare token list, convert to wide
        cas_element_csv['begin'] = cas_element_csv['begin'].str.replace("\"", "").astype(int)
        cas_element_csv['end'] = cas_element_csv['end'].str.replace("\"", "").astype(int)
        cas_element_csv['xmid'] = cas_element_csv['xmid'].str.replace("\"", "").astype(int)

        token_csv = cas_element_csv[cas_element_csv['type'] == 'Token']
        token_csv['token'] =  ''

        #add sentence id
        token_csv['sent_id'] = 'nan'

        sentence_csv = cas_element_csv[cas_element_csv['type'] == 'Sentence']
        token_anno_csv = cas_element_csv[(cas_element_csv['tagQualifier'] == 'custom') &
                                         (cas_element_csv['fname'] != 'relation')]

        for i in range(0,len(token_csv)):
            token_csv['token'].iloc[i] = cas_text[token_csv['begin'].iloc[i]+1:token_csv['end'].iloc[i]+1]
            sent_id= sentence_csv['xmid'][ ( sentence_csv['begin'] <= token_csv['begin'].iloc[i]) &
                                     ( sentence_csv['end'] >= token_csv['begin'].iloc[i])]
            token_csv['sent_id'].iloc[i] = sent_id.values[0]



        #add annotations
        # add annotations for tokens to token list
        # restriction: only 1 annotation for token of same type.fname
        annotation_labels = pd.DataFrame(columns=['type', 'fname'])

        #annotation all type, fname, use for wide format
        for tdesc in cas.typesystem.getAllTypeDesc():
            for fdesc in tdesc.getAllFeature():
                if str(tdesc.name).startswith("webanno.custom."):
                    tmp = pd.DataFrame.from_dict({'type': [tdesc.name], 'fname': [fdesc.name]})
                    annotation_labels = annotation_labels.append(tmp, ignore_index=True)

        annotation_labels['type'] = annotation_labels['type'].str.replace("webanno.custom.", "")

        tmp = annotation_labels.merge(cas_element_csv[cas_element_csv['tagQualifier'] == 'custom'],
                                      left_on=['type', 'fname'],
                                      right_on=['type', 'fname'], how='left')

        #assert only one per fname value, span
        #To do: remove conversion should already be data frame
        token_csv = pd.DataFrame(token_csv)
        for anno in range(0, len(tmp)):
            colname = tmp['type'][anno] + '.' + tmp['fname'][anno]
            token_csv[colname] = ''
            tmp_anno = (token_csv['begin'] >= tmp['begin'][anno]) & (token_csv['begin'] < tmp['end'][anno])
            token_csv.loc[tmp_anno, colname] = tmp['fname_val'][anno]

        return token_csv, cas_element_csv


    "This method returns the tag qualifier for a given type"
    def __getTagQualifier(self,giventype):
        domain = giventype[0:giventype.rfind(".")]
        for nselem in self.__xmlnsDictList:
            if nselem['namespace'] == domain:
                tagQualifier = nselem['tagQualifier']
        return tagQualifier

def escape(s):
    return quoteattr(str(s))