'''
Created on Jan 23, 2017

@author: Dibyojyoti
'''
import os
import sys

from xml.sax.saxutils import quoteattr

from pycas.cas.core.FeatureStructure import FeatureStructure
from pycas.type.cas.TypeDescription import TypeDescription

class XmiWriter(object):
    '''
    This class writes a CAS object in the XMI format
    '''
    def __init__(self):
        '''
        Constructor
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
    def writeToString(self, cas):
           return self.__toString(cas)

    "This method writes the CAS as a XMI file to the given path(file name also included in the path)"
    def write(self,cas,filepath):
        try:
            if not (os.path.dirname(filepath) == ""):
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, "w") as f:
                f.write(self.__toString(cas))
        except:
            print('Something went wrong! cannot create file',os.path.basename(filepath),'in',os.path.dirname(filepath))
            sys.exit(1)
    "This internal method generates Strings from the CAS object so that it can be written"
    def __toString(self,cas):
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
        self.__xmlnsDictList.append({'namespace': 'www.omg.org', 'tagQualifier': 'xmi', 'domainurl': 'http://www.omg.org/XMI'})

        #add XMI root tag name and qualifier
        xmistr = '<?xml version="1.0" encoding="UTF-8"?>'+'<'+self.__tagQualifier+':'+self.__tagName

        #add name spaces
        for nselem in self.__xmlnsDictList:
            xmistr =xmistr+' xmlns:'+nselem['tagQualifier']+'='+escape(nselem['domainurl'])
        #close root tag with version
        xmistr = xmistr+' xmi:version='+escape(self.__version)+'>'

        #add casnull
        xmistr = xmistr+'<cas:NULL xmi:id="0"/>'

        fsNotInIndexListCheck= []
        indexedFsIdArray = []
        #get the list of annotations or FS in the CAS
        for element in cas.getAnnotationIndex():
            #add cas:null element
            if( element.FStype.name == 'uima.cas.NULL'):
                domlist=element.FStype.name.split('.')
                tagName=domlist[len(domlist)-1]
                tagQualifier=self.__getTagQualifier(element.FStype.name)
                casnull='<'+tagQualifier+':'+tagName+' xmi:id='+escape(element.FSid)+'/>'
                #add the id to the indexedFsIdArray to record that this FS is already processed
                indexedFsIdArray.append(element.FSid)
                xmistr = xmistr+casnull

            #add cas:sofa element
            if( element.FStype.name == 'uima.cas.Sofa'):
                domlist=element.FStype.name.split('.')
                tagName=domlist[len(domlist)-1]
                tagQualifier=self.__getTagQualifier(element.FStype.name)
                cassofa='<'+tagQualifier+':'+tagName+' xmi:id='+escape(element.FSid)+' sofaNum='+escape(element.sofaNum)+' sofaID='+ escape(element.sofaID)+' mimeType='+ escape(element.mimeType)+ ' sofaString='+escape(element.sofaString)+'/>'
                #add the id to the indexedFsIdArray to record that this FS is already processed
                indexedFsIdArray.append(int(element.FSid))
                xmistr = xmistr+cassofa

            #add other feature structures
            else:
                domlist=element.FStype.name.split('.')
                tagName=domlist[len(domlist)-1]
                tagQualifier=self.__getTagQualifier(element.FStype.name)
                casfs='<'+tagQualifier+':'+tagName+' xmi:id='+escape(element.FSid)+''
                #add the id to the indexedFsIdArray to record that this FS is already processed
                indexedFsIdArray.append(element.FSid)
                fspoprs=''
                sofa=''
                begin=''
                end=''
                #if the FS has features iterate through list of features and serialize
                if(len(element.getFeatures()) >= 1):
                    for fdict in element.getFeatureValsAsDictList():
                        for fname,fval in fdict.items():
                            #get the sofa feature
                            if(fname =='sofa'):
                                sofa = ' sofa=' +escape(fval.FSid)+''
                            #get the begin
                            elif(fname == 'begin'):
                                begin = ' begin=' +escape(fval)+''
                            #get the end
                            elif(fname == 'end'):
                                end = ' end=' +escape(fval)+''
                            #for all other features
                            else:
                                #if feature value is not a list
                                if not type(fval) is list:
                                    #if its FS take FSid and add the FS to the fsNotInIndexListCheck
                                    if (isinstance(fval,TypeDescription) and isinstance(fval,FeatureStructure)):
                                        fspoprs=fspoprs+' '+fname+'='+escape(fval.FSid)
                                        fsNotInIndexListCheck.append(fval)
                                    else:
                                        fspoprs=fspoprs+' '+fname+'='+escape(fval)
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
                                    fspoprs=fspoprs+' '+fname+'='+ escape(listval)+''
                                else:
                                    raise TypeError('type of feature',fname,'not recognized')

                #add attributes with vale
                casfs= casfs + sofa + begin + end +  fspoprs
                #add closing
                casfs = casfs+'/>'

                xmistr = xmistr + casfs
        #Now check the FS added in fsNotInIndexListCheck if they are processed means in indexedFsIdArray ignore, otherwise process
        #this is done because all the referenced FS are not added in index of the CAS
        for fs in fsNotInIndexListCheck:
            if( not fs.FSid in indexedFsIdArray):
                domlist=fs.FStype.name.split('.')
                tagName=domlist[len(domlist)-1]
                tagQualifier=self.__getTagQualifier(fs.FStype.name)
                casfs='<'+tagQualifier+':'+tagName+' xmi:id='+escape(fs.FSid)+''

                fspoprs=''
                sofa=''
                begin=''
                end=''
                #if the FS has features iterate through list of features and serialize
                if(len(fs.getFeatures()) >= 1):
                    for fdict in fs.getFeatureValsAsDictList():
                        for fname,fval in fdict.items():
                            if(fname =='sofa'):
                                sofa = ' sofa=' +escape(fval.FSid)+''
                            #get the begin
                            elif(fname == 'begin'):
                                begin = ' begin=' +escape(fval)+''
                            #get the end
                            elif(fname == 'end'):
                                end = ' end=' +escape(fval)+''
                            else:
                                if not type(fval) is list:
                                    #if its FS take FSid
                                    if (isinstance(fval,TypeDescription) and isinstance(fval,FeatureStructure)):
                                        fspoprs=fspoprs+' '+fname+'='+escape(fval.FSid)+''
                                    else:
                                        fspoprs=fspoprs+' '+fname+'='+escape(fval)+''
                                elif type(fval) is list:
                                    listval=''
                                    for valelement in fval:
                                        #if its FS
                                        if (isinstance(valelement,TypeDescription) and isinstance(valelement,FeatureStructure)):
                                            listval = escape(valelement.FSid) if (listval == '') else listval+' '+escape(valelement.FSid)
                                        else:
                                            listval = escape(valelement) if (listval == '') else listval+' '+escape(valelement)
                                    fspoprs=fspoprs+' '+fname+'='+listval+''
                                else:
                                    raise TypeError('type of feature',fname,'not recognized')

                #add attributes with vale
                casfs= casfs + sofa + begin + end +fspoprs
                #add closing
                casfs = casfs+'/>'

                xmistr = xmistr + casfs

        #add cas:View element
        casview = '<cas:View'+' sofa='+ escape(cas.sofaFS.FSid)
        memlist = ' '.join(sorted([str(element.FSid) for element in cas.getSofaCasView() if element.FSid != cas.sofaFS.FSid], key=int ))

        casview = casview + ' members='+ escape(memlist)+'/>'

        xmistr = xmistr + casview

        #add closing xmi root tag
        xmistr = xmistr+'</'+self.__tagQualifier+':'+self.__tagName+'>'

        return xmistr
    "This method returns the tag qualifier for a given type"
    def __getTagQualifier(self,giventype):
        domain = giventype[0:giventype.rfind(".")]
        for nselem in self.__xmlnsDictList:
            if nselem['namespace'] == domain:
                tagQualifier = nselem['tagQualifier']
        return tagQualifier

def escape(s):
    return quoteattr(str(s))