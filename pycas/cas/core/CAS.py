'''
Created on Jan 19, 2017

@author: Dibyojyoti
'''
from pycas.cas.core.SofaFS import SofaFS
from pycas.cas.core.TOP import TOP
from pycas.cas.core.Annotation import Annotation

class CAS(object):
    '''
    This class represents a UIMA CAS
    '''
    def __init__(self, typesystem):
        '''
        Constructor
        '''
        #set type system object
        self.typesystem = typesystem
        #holds the indexed feature structures
        self.__FSArray = []
        #counter to add id to each feature structure created in the class, if user supplied id given it will be accepted if available
        #if not supplied a unique id will be given
        self.__idCounter = 0
        #list to hold the numeric values that has been used as ids 
        self.__idArray = []
        #create sofa FS
        self.__sofaFS = self.createSofaFS('uima.cas.Sofa',{'sofaNum': 1, 'sofaID': '_InitialView','mimeType': 'text'})
        self.__DocumentFS=None
        
    "Returns documentText"
    @property
    def documentText(self):
        return self.__sofaFS.sofaString
    "Sets documentText"
    @documentText.setter
    def documentText(self, text):
        self.__sofaFS.sofaString = text
    "Returns sofaMimeType"
    @property
    def sofaMimeType(self):
        return self.__sofaFS.mimeType
    "Sets sofaMimeType"
    @sofaMimeType.setter
    def sofaMimeType(self, value):
        self.__sofaFS.mimeType = value
    "Returns documentLanguage"
    @property
    def documentLanguage(self):
        return self.__documentLanguage
    "Sets documentLanguage"
    @documentLanguage.setter
    def documentLanguage(self, text):
        self.__documentLanguage = text

    "Returns type system"
    @property
    def typesystem(self):
        return self.__typesystem
    "Sets type system"
    @typesystem.setter
    def typesystem(self, tspath):
        self.__typesystem = tspath
    "This method returns the counter to set id"
    def __getCounter(self,fsid,dictid):
        #if Fsid attribute is not provided or 'id' is not supplied in feature dict
        if(fsid == -1 and dictid==None):
            while True:
                self.__idCounter= self.__idCounter+1
                if not (self.__idCounter in self.__idArray):
                    break
        #if Fsid attribute is provided and 'id' is supplied in feature dict    
        elif(not fsid == -1 and not dictid==None):
            raise ValueError('FSid and id in feature dict, both not allowed')
        #if Fsid attribute is provided but 'id' is not supplied in feature dict
        elif(not fsid == -1 and dictid==None):
            if(fsid in self.__idArray ):
                raise ValueError(fsid,'as FSid is already occupied')
            else:
                self.__idCounter = fsid
        #if Fsid attribute is not provided but 'id' is supplied in feature dict        
        elif(fsid == -1 and not dictid==None):
            if not (type(dictid) is int):
                raise ValueError('id should ve non negative integer')
            elif(dictid<0):
                raise ValueError('id should ve non negative integer')
            elif(dictid in self.__idArray):
                raise ValueError(dictid,'as FSid is already occupied')
            else:
                self.__idCounter = dictid
        self.__idArray.append(self.__idCounter)        
        return self.__idCounter
    "creates and returns document annotation or FS"
    def createDocumentAnnotation(self,typeName,length,featureDict,FSid=-1):
        featureDict['begin'] = 0
        featureDict['end'] = length
        if(not featureDict['language'] == None):
            self.__documentLanguage = featureDict['language']
        self.__DocumentFS= self.createAnnotation(typeName, featureDict,FSid)
        return self.__DocumentFS
    "returns document FS"
    def getDocumentAnnotation(self):
        return self.__DocumentFS 
    '''
    creates and returns FS of class Annotation , needs begin and end name-value pair in dictionary
    Args: 
        typeName : fully qualified name of the type as string
        featureDict: dictionary of name-value pair of features
        FSid : id of feature structure, optional, if not given automatic id is given  
    '''
    def createAnnotation(self, typeName, featureDict,FSid=-1):
        fsAnnotationType = self.typesystem.getType(typeName)
        if 'id' in featureDict:
            fsid = self.__getCounter(FSid,featureDict['id'])
        else:
            fsid = self.__getCounter(FSid,None)
        annotationFs = Annotation(fsAnnotationType,fsid,self.typesystem)
        annotationFs.CAS = self        
        annotationFs.sofa = self.sofaFS

        if not 'begin' in featureDict:
            raise ValueError('feature begin must be given')
            "annotationFs.begin = featureDict['begin']"
        if not 'end' in featureDict:
            raise ValueError('feature end must be given')
        if not featureDict == None:
            for key in featureDict:
                if not ( key == 'id'):     
                    setattr(annotationFs,key,featureDict[key])
        return annotationFs
    '''
    creates and returns FS of class TOP
    Args: 
        typeName : fully qualified name of the type as string
        featureDict: dictionary of name-value pair of features
        FSid : id of feature structure, optional, if not given automatic id is given  
    '''    
    def createFS(self, typeName,featureDict=None,FSid=-1):
        fsTopType = self.typesystem.getType(typeName)
        if ((not featureDict == None) and ('id' in featureDict)):
            fsid = self.__getCounter(FSid,featureDict['id'])
        else:
            fsid = self.__getCounter(FSid,None)
  
        topFs = TOP(fsTopType,fsid,self.typesystem)
        topFs.CAS = self
        if not featureDict == None:
            for key in featureDict:
                if not (key == 'id'):
                    setattr(topFs,key,featureDict[key])
        return topFs
    '''
    creates and returns sofa FS 
    Args: 
        typeName : fully qualified name of the type as string
        featureDict: dictionary of name-value pair of features(optional)
        FSid : id of feature structure, optional, if not given automatic id is given  
    '''        
    def createSofaFS(self, typeName, featureDict=None,FSid=-1):
        fsSofaType = self.typesystem.getType(typeName)
        if ((not featureDict == None) and ('id' in featureDict)):
            fsid = self.__getCounter(FSid,featureDict['id'])
        else:
            fsid = self.__getCounter(FSid,None)    

        sofaFs = SofaFS(fsSofaType,fsid)
        sofaFs.CAS = self
        if not featureDict == None:
            for key in featureDict:
                if not (key == 'id'):
                    setattr(sofaFs,key,featureDict[key])
        self.__sofaFS = sofaFs
        self.addToIndex(self.__sofaFS)
        return sofaFs
    "returns a list of FS which matches the type name"
    def getAnnotation(self,typeName):
        fsList=[]
        for fs in self.__FSArray:
            if(fs.FStype.name == typeName):
                fsList.append(fs)
        return fsList
    "adds the given FS to index"    
    def addToIndex(self,fs):
        self.__FSArray.append(fs)
    "removes a given FS from index"    
    def removeFromIndex(self,fs):
        for element in self.__FSArray:
            if(element.FSType.name == fs.FStype.name and element.FSid == fs.FSid):
                self.__FSArray.remove(element)
                self.freeId(fs.FSid)
    "frees an id"
    def freeId(self,num):
        self.__idArray.remove(num)    
    "Returns sofaFS"
    @property
    def sofaFS(self):
        return self.__sofaFS
    "returns list of FS in index "
    def getAnnotationIndex(self):
        return self.__FSArray
    "returns sofa cas view"
    def getSofaCasView(self):
        return self.getAnnotationIndex()
    
        
