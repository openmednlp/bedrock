'''
Created on Jan 23, 2017

@author: Dibyojyoti
'''
from pycas.cas.parse.CasXmiParser import CasXmiParser
from pycas.cas.core.CAS import CAS
from pycas.type.cas.CAS_Type import CAS_Type
from pycas.type.cas.TypeSystemFactory import TypeSystemFactory
from pycas.type.cas.TypeDescription import TypeDescription

class CasFactory(object):
    '''
    This class creates a CASS object from a given CAS xmi file and type system file
    '''

    def __init__(self):
        '''
        Constructor
        '''
    '''
    returns a CAS object
    Args: 
        xmifilepath : cas xmi file path
        typefilepath : type system xml file path
    '''
    def buildCAS(self,xmifilepath,typefilepath):    
        #create type ystem object
        typesystem = TypeSystemFactory.readTypeSystem(self, typefilepath)
        #create a CAS object
        cas = CAS(typesystem)
        #create cas xmi perser object to fetch elements from xmi file
        casXmiParser = CasXmiParser()
        casXmiParser.setXmiAsFile(xmifilepath)
        return self.__build(cas, casXmiParser)

    def buildCASfromString(self,xmistring,typefilepath):    
        #create type ystem object
        typesystem = TypeSystemFactory.readTypeSystem(self, typefilepath)
        #create a CAS object
        cas = CAS(typesystem)
        #create cas xmi perser object to fetch elements from xmi file
        casXmiParser = CasXmiParser()
        casXmiParser.setXmiAsString(xmistring)
        return self.__build(cas, casXmiParser)
    
    def buildCASfromStrings(self, xmistring, typesysstemString):
        # create type ystem object
        typesystem = TypeSystemFactory.readTypeSystemString(self, typesysstemString)
        # create a CAS object
        cas = CAS(typesystem)
        # create cas xmi perser object to fetch elements from xmi file
        casXmiParser = CasXmiParser()
        casXmiParser.setXmiAsString(xmistring)
        return self.__build(cas, casXmiParser)

    def __build(self,cas,casXmiParser):
        #get xmi root element as string
        rootstr=casXmiParser.getRootElementAsString()
        #get cas sofa element
        for k in casXmiParser.getChildAttributesAsDict(casXmiParser.getCasSofaChild()):
            if(casXmiParser.getLocalname(k) == 'id'):
                cas.freeId(cas.sofaFS.FSid)
                cas.sofaFS.FSid = casXmiParser.getChildAttributesAsDict(casXmiParser.getCasSofaChild()).get(k)                
            if(casXmiParser.getLocalname(k) == 'sofaNum'):
                pass
            elif(casXmiParser.getLocalname(k) == 'sofaID'):
                pass
            elif(casXmiParser.getLocalname(k) == 'mimeType'):
                cas.sofaMimeType = casXmiParser.getChildAttributesAsDict(casXmiParser.getCasSofaChild()).get(k)
            elif(casXmiParser.getLocalname(k) == 'sofaString'):
                cas.documentText = casXmiParser.getChildAttributesAsDict(casXmiParser.getCasSofaChild()).get(k)

        #"set type system file path for other feature structures"
        #these contains the map of features names which refers other FS with FSid and the FS in which the feature is to be added 
        FtobeAddedDict = []
        FSnotInIndexList = []
        #loop each non cas feature structure elements 
        for fs in casXmiParser.getNonCasChildren():
            if not (casXmiParser.getLocalname(fs) == 'XMI'): #or
                    #casXmiParser.getLocalname(fs) == 'TagsetDescription' or
                    #  casXmiParser.getLocalname(fs) == 'DocumentMetaData'):
                #get the name space url of the element and convert into domain
                domain = casXmiParser.getNamespace(fs)[8:casXmiParser.getNamespace(fs).index('.ecore')].replace('/','.')
                domain = domain+'.'+casXmiParser.getLocalname(fs)
                #get the type description from type system for the domain
                typedesc = cas.typesystem.getType(domain)
                if(typedesc == None):
                    raise ValueError('bad xml',casXmiParser.getNamespace,'not in type system' )
                    return
                #loop through attributes of the feature structure element, add build feature dict
                featureDict = {}
                # list to hold the attributes and values those refer to other FS
                referenceList = {}
                for k in casXmiParser.getChildAttributesAsDict(fs):
                    if(casXmiParser.getLocalname(k) == 'id'):
                        featureDict[casXmiParser.getLocalname(k)] = int(casXmiParser.getChildAttributesAsDict(fs).get(k))
                    #add sofa attribute
                    elif(casXmiParser.getLocalname(k) == 'sofa'):
                        featureDict[casXmiParser.getLocalname(k)] = cas.sofaFS
                    #add begin and end attribute
                    elif((casXmiParser.getLocalname(k) == 'begin') or (casXmiParser.getLocalname(k) == 'end')):
                        featureDict[casXmiParser.getLocalname(k)] = int(casXmiParser.getChildAttributesAsDict(fs).get(k))
                    #add other attributes
                    else:
                        #get the attribute value
                        value = casXmiParser.getChildAttributesAsDict(fs).get(k)
                        #get the feature description from type system
                        theFeature = cas.typesystem.getFeature(casXmiParser.getLocalname(k),domain)
                        if(theFeature == None):
                            raise ValueError('bad xml,', casXmiParser.getLocalname(k),'is not a feature of',casXmiParser.getLocalname(fs))
                            return
                        #if both rang and element type does not exists, throw error
                        if((theFeature.rangeType == None) and (theFeature.elementType == None)):
                            raise ValueError(casXmiParser.getLocalname(k),'range type and element type does not exists in type system')
                            return
                            
                        # if range type does not exist, determine type from element type'
                        if(theFeature.rangeType == None):
                            #if type is cas primitive just add it to the feature dictionary
                            if (theFeature.elementType in (CAS_Type.TYPE_NAME_BOOLEAN,CAS_Type.TYPE_NAME_FLOAT,
                                CAS_Type.TYPE_NAME_DOUBLE,CAS_Type.TYPE_NAME_INTEGER,CAS_Type.TYPE_NAME_LONG,
                                CAS_Type.TYPE_NAME_STRING)):
                                
                                featureDict[casXmiParser.getLocalname(k)] = value
                            else:
                                'value is a FS, so the referenced FS may not b created now , save it to referenceList'
                                referenceList[casXmiParser.getLocalname(k)] = value 
                        #if rang type is FSARRAY determine type from element type
                        elif((not theFeature.rangeType == None) and
                             (isinstance(theFeature.rangeType,TypeDescription)) and 
                             (theFeature.rangeType.name == CAS_Type.TYPE_NAME_FSARRAY)):
                            #if type is cas primitive just add it to the feature dictionary
                            #even if its a list just send the string the TOP.__setAttribute will convert to list
                            if (theFeature.elementType in (CAS_Type.TYPE_NAME_BOOLEAN,CAS_Type.TYPE_NAME_FLOAT,
                                CAS_Type.TYPE_NAME_DOUBLE,CAS_Type.TYPE_NAME_INTEGER,CAS_Type.TYPE_NAME_LONG,
                                CAS_Type.TYPE_NAME_STRING)):

                                featureDict[casXmiParser.getLocalname(k)] = value
                            else:
                                'value is a FS array, so the referenced FS may not b created now , save it to referenceList'
                                referenceList[casXmiParser.getLocalname(k)] = value   
                        #'if rang type is not FSARRAY determine type from range type'
                        else:
                            #if type is cas primitive just add it to the feature dictionary
                            #even if its a list just send the string the TOP.__setAttribute will convert to list
                            if (theFeature.rangeType in (CAS_Type.TYPE_NAME_BOOLEAN,CAS_Type.TYPE_NAME_FLOAT,
                                CAS_Type.TYPE_NAME_DOUBLE,CAS_Type.TYPE_NAME_INTEGER,CAS_Type.TYPE_NAME_LONG,
                                CAS_Type.TYPE_NAME_STRING)):

                                featureDict[casXmiParser.getLocalname(k)] = value
                            else:
                                'value is a FS, so the referenced FS may not b created now , save it to referenceList'
                                referenceList[casXmiParser.getLocalname(k)] = value
                #if the element's super type is TOP in type system create a TOP FS, otherwise create a Annotation FS                
                if not(typedesc.superType =='uima.cas.TOP'):
                    if('DocumentMetaData' in domain):
                        anewFs =  cas.createDocumentAnnotation(domain,len(cas.documentText),featureDict) 
                    else:
                        anewFs=  cas.createAnnotation(domain,featureDict)
                    cas.addToIndex(anewFs)
                else:
                    anewFs=  cas.createFS(domain,featureDict)
                    FSnotInIndexList.append(anewFs)

                #add to the list of reference to be added after all FS are created from referenceList
                for e in referenceList:
                    FtobeAddedDict.append({'refby': anewFs.FSid,'fname': e,'refto': referenceList[e]})
                
        #set the references
        #iterate the features to be added dict
        for element in FtobeAddedDict:
            #initialize FS reference list
            refFS = []
            refto = None
            refby = None
            #if reference to string contains list of ids , create a int list of ids
            refarray = []
            if ' ' in element['refto']:
                refarray = element['refto'].split()
                refarray = list(map(int, refarray))                
            #iterate through all FS added to index in CAS    
            for fs in cas.getAnnotationIndex():
                # find the FS for reference ids in CAS, if there are more than one references
                if len(refarray) > 0 :
                    for ref in refarray:
                        if(fs.FSid == ref):
                            refFS.append(fs)
                #if there is only one reference             
                else:
                    if(fs.FSid == int(element['refto'])):
                        refto = fs
                        
                if(fs.FSid == int(element['refby'])):
                    refby = fs
            if len(refFS) > 0:
                setattr(refby,element['fname'],refFS)
            if not refto == None:
                setattr(refby,element['fname'],refto)
                    
        #set the references, #iterate the features to be added dict
        
        for element in FtobeAddedDict:
            #initialize FS reference list
            refFS = []
            refto = None
            refby = None
            for fs in cas.getAnnotationIndex():
                if(fs.FSid == int(element['refby'])):
                    refby = fs
            #if reference to string contains list of ids , create a int list of ids
            refarray = []
            if ' ' in element['refto']:
                refarray = element['refto'].split()
                refarray = list(map(int, refarray))                
            #iterate through all FS added to index in CAS    
            for fs in FSnotInIndexList:
                # find the FS for reference ids in CAS, if there are more than one references
                if len(refarray) > 0 :
                    for ref in refarray:
                        if(fs.FSid == ref):
                            refFS.append(fs)
                #if there is only one reference             
                else:
                    if(fs.FSid == int(element['refto'])):
                        refto = fs
            if len(refFS) > 0:
                setattr(refby,element['fname'],refFS)
            if not refto == None:
                setattr(refby,element['fname'],refto)        
        
        return cas            
    
