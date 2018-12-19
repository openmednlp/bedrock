'''
Created on Dec 17, 2016

@author: Dibyojyoti
'''
from pycas.cas.core.FeatureStructure import FeatureStructure
from pycas.type.cas.Feature import Feature
from pycas.type.cas.CAS_Type import CAS_Type
from pycas.type.cas.TypeDescription import TypeDescription

class TOP(FeatureStructure,TypeDescription):
    '''
    This class implements the setValue and getValue method of FeatureStructure,
    provides means of storing features   
    Args: 
        FStype (TypeDescrption): type of feature structure
        FSid : id of feature structure
        typeSystem (TypeSystem): type system object  
    '''
    def __init__(self,FStype,FSid,typeSystem):

        '''
        Constructor
        '''
        self.__CAS = None
        "holds feature objects as list"
        self.__featureIndex = []
        "holds feature name and feature value as list of dictionary"
        self.__featureValueDict = []
        self.FSid = FSid
        self.typeSystem = typeSystem        
        #set the FStype, an object of type TypeDescription
        self.FStype = FStype
    "This method is called to set generic properties, it checks if the property exists for the FS and converts property to Feature"    
    def __setProperty(self,propertyName,value):
        
        "check if the property is a feature of the FS in type system "
        "if the propertyName is part of the type then only set the feature, use the returned type to set rangeType and elementType"
        theFeature = self.typeSystem.getFeature(propertyName,self.FStype.name)
        if(theFeature == None):
            raise ValueError(propertyName,' is not part of type',self.FStype.name)
        else:
            #if feature has range type only call setListValue
            if ((not theFeature.rangeType == None) and (theFeature.elementType == None)):

                #if range type is primitive CAS type
                if(theFeature.rangeType in (CAS_Type.TYPE_NAME_BOOLEAN ,CAS_Type.TYPE_NAME_FLOAT, 
                   CAS_Type.TYPE_NAME_DOUBLE,CAS_Type.TYPE_NAME_INTEGER,CAS_Type.TYPE_NAME_LONG,CAS_Type.TYPE_NAME_STRING)):                    
                    #if its a single value of type boolean convert to lower (False->false,True->true) string
                    #if its a single value of other type convert to string
                    #so for single value user don't have to supply a string or list of string, and don't have to care if the type is rangeType
                    if type(value) is bool:
                        valuelist = str(value).lower().split()
                    else:
                        valuelist = str(value).split()
                    self.setListValue(theFeature, theFeature.rangeType,valuelist)    
                #if range type is non primitive CAS type means Top type        
                else:
                    #expected that user will send a value of FS with same type as feature specified in type system
                    #if its a single value convert to list of FS
                    #so for single value FS user don't have to supply a list of FS, and don't have to care if the type is rangeType
                    if isinstance(value,TypeDescription):                        
                        valuelist = []
                        valuelist.append(value)
                    #expect a list of FS from user
                    else:
                        valuelist = []
                        valuelist = value                    
                    self.setListValue(theFeature, theFeature.rangeType,valuelist)             
            #if feature has element type only call proper setter as per type    
            elif ((theFeature.rangeType == None) and (not theFeature.elementType == None)):
                if (theFeature.elementType == CAS_Type.TYPE_NAME_BOOLEAN):
                    self.setBoolValue(theFeature,value)
                elif (theFeature.elementType == CAS_Type.TYPE_NAME_FLOAT):
                    self.setFloatValue(theFeature,value)
                elif (theFeature.elementType == CAS_Type.TYPE_NAME_DOUBLE):
                    self.setFloatValue(theFeature,value)
                elif (theFeature.elementType == CAS_Type.TYPE_NAME_INTEGER):
                    self.setIntValue(theFeature,value)
                elif (theFeature.elementType == CAS_Type.TYPE_NAME_LONG):
                    self.setIntValue(theFeature,value)
                elif (theFeature.elementType == CAS_Type.TYPE_NAME_STRING):
                    self.setStringValue(theFeature,value)
                else:
                    #expected that user will send a value of FS with same type as feature specified in type system
                    self.setFeatureValue(theFeature,value)
            #if feature has both element and range type        
            elif ((not theFeature.rangeType == None) and ( not theFeature.elementType == None)):
                #if rangeVal is not FSArray the combination is not valid and makes no sense, treat is as only rangeVal
                if ( not theFeature.rangeType.name == CAS_Type.TYPE_NAME_FSARRAY):
                    #if range type is primitive CAS type
                    if(theFeature.rangeType in (CAS_Type.TYPE_NAME_BOOLEAN,CAS_Type.TYPE_NAME_FLOAT, 
                       CAS_Type.TYPE_NAME_DOUBLE,CAS_Type.TYPE_NAME_INTEGER,CAS_Type.TYPE_NAME_LONG,CAS_Type.TYPE_NAME_STRING)):
                        if type(value) is bool:
                            valuelist = str(value).lower().split()
                        else:
                            valuelist = str(value).split()
                        self.setListValue(theFeature, theFeature.rangeType,valuelist)
                    #if its a FS
                    else:
                        if isinstance(value,int):
                            
                            valuelist = []
                            valuelist.append(value)
                        else:
                            valuelist = []
                            valuelist = value
                        
                        self.setListValue(theFeature, theFeature.rangeType,valuelist)                                 
                #if range type is FSArray, check element type
                else:
                    #if element type is CAS primitive
                    if(theFeature.elementType in(CAS_Type.TYPE_NAME_BOOLEAN,CAS_Type.TYPE_NAME_FLOAT,CAS_Type.TYPE_NAME_DOUBLE,
                        CAS_Type.TYPE_NAME_INTEGER,CAS_Type.TYPE_NAME_LONG,CAS_Type.TYPE_NAME_STRING)):
                        if type(value) is bool:
                            valuelist = str(value).lower().split()
                        else:
                            valuelist = str(value).split()
                        self.setListValue(theFeature, theFeature.elementType,valuelist)    
                    else:
                        if isinstance(value,int):
                            
                            valuelist = []
                            valuelist.append(value)
                        else:
                            valuelist = []
                            valuelist = value
                        self.setListValue(theFeature, theFeature.elementType,valuelist)                                 
                        
            #if feature has none element or range type    
            else:
                raise TypeError('can not create feature for',propertyName,', no type found in type system')
    "This method id called to get value of generic properties, it checks if the property exists for the FS and converts property to Feature"        
    def __getProperty(self,propertyName):
        "check if the property is a feature of the FS in type system "
        "if the propertyName is part of the type then only set the feature, use the returned type to set rangeType and elementType"
        theFeature = self.typeSystem.getFeature(propertyName,self.FStype.name)
        if(theFeature == None):
            raise ValueError(propertyName,' is not part of type',self.FStype.name)
        else:
            #if feature has range type only call getListValue
            if ((not theFeature.rangeType == None) and (theFeature.elementType == None)):
                #if range type is primitive CAS type return a list value as string
                if(theFeature.rangeType in (CAS_Type.TYPE_NAME_BOOLEAN ,CAS_Type.TYPE_NAME_FLOAT, 
                   CAS_Type.TYPE_NAME_DOUBLE,CAS_Type.TYPE_NAME_INTEGER,CAS_Type.TYPE_NAME_LONG,CAS_Type.TYPE_NAME_STRING)):
                    return ' '.join(self.getListValue(theFeature))    
                #if range type is non primitive CAS type means Top type, return as it is
                else:
                    return self.getListValue(theFeature)             
            #if feature has element type only call proper setter as per type    
            elif ((theFeature.rangeType == None) and (not theFeature.elementType == None)):
                #set element type of feature
                if (theFeature.elementType == CAS_Type.TYPE_NAME_BOOLEAN):
                    return self.getBoolValue(theFeature)
                elif (theFeature.elementType == CAS_Type.TYPE_NAME_FLOAT):
                    return self.getFloatValue(theFeature)
                elif (theFeature.elementType == CAS_Type.TYPE_NAME_DOUBLE):
                    return self.getFloatValue(theFeature)
                elif (theFeature.elementType == CAS_Type.TYPE_NAME_INTEGER):
                    return self.getIntValue(theFeature)
                elif (theFeature.elementType == CAS_Type.TYPE_NAME_LONG):
                    return self.getIntValue(theFeature)
                elif (theFeature.elementType == CAS_Type.TYPE_NAME_STRING):
                    return self.getStringValue(theFeature)
                else:
                    return self.getFeatureValue(theFeature)
            #if feature has both element and range type
            elif ((not theFeature.rangeType == None) and ( not theFeature.elementType == None)):
                #if rangeVal is not FSArray the combination is not valid and makes no sense, treat is as only rangeVal
                if ( not theFeature.rangeType.name == CAS_Type.TYPE_NAME_FSARRAY):
                    #if range type is primitive CAS type
                    if(theFeature.rangeType in (CAS_Type.TYPE_NAME_BOOLEAN ,CAS_Type.TYPE_NAME_FLOAT, 
                   CAS_Type.TYPE_NAME_DOUBLE,CAS_Type.TYPE_NAME_INTEGER,CAS_Type.TYPE_NAME_LONG,CAS_Type.TYPE_NAME_STRING)):
                        return ' '.join(self.getListValue(theFeature))
                    #if its a FS
                    else:
                        return self.getListValue(theFeature)                                 
                #if range type is FSArray, check element type
                else:
                    #if element type is CAS primitive
                    if(theFeature.elementType in (CAS_Type.TYPE_NAME_BOOLEAN ,CAS_Type.TYPE_NAME_FLOAT, 
                   CAS_Type.TYPE_NAME_DOUBLE,CAS_Type.TYPE_NAME_INTEGER,CAS_Type.TYPE_NAME_LONG,CAS_Type.TYPE_NAME_STRING)):
                        return ' '.join(self.getListValue(theFeature))    
                    else:
                        return self.getListValue(theFeature)                                 
            #if feature has none element or range type    
            else:
                raise TypeError('can not create feature for',propertyName,', no type found in type system')        
    "This method returns value of given features in FS"        
    def getValOfFeature(self,feature):
        "check if the property is a feature of the FS in type system "
        "if the propertyName is part of the type then only set the feature, use the returned type to set rangeType and elementType"
        if not isinstance(feature,Feature):
            raise ValueError('please provide a feature to getFeature(feature)')
        else:
            #if feature has range type only call getListValue
            if ((not feature.rangeType == None) and (feature.elementType == None)):
                #if range type is primitive CAS type return a list value as string
                if(feature.rangeType == CAS_Type.TYPE_NAME_BOOLEAN or feature.rangeType == CAS_Type.TYPE_NAME_FLOAT or 
                   feature.rangeType == CAS_Type.TYPE_NAME_DOUBLE or feature.rangeType == CAS_Type.TYPE_NAME_INTEGER or 
                   feature.rangeType == CAS_Type.TYPE_NAME_LONG or feature.rangeType == CAS_Type.TYPE_NAME_STRING):
                    return ' '.join(self.getListValue(feature))    
                #if range type is non primitive CAS type means Top type, return as it is
                elif type(feature.rangeType) is  TypeDescription:
                    return self.getListValue(feature)
                else:
                    raise ValueError('feature type not recognized')
                    return
            #if feature has element type only call proper setter as per type    
            elif ((feature.rangeType == None) and (not feature.elementType == None)):
                if (feature.elementType == CAS_Type.TYPE_NAME_BOOLEAN):
                    return self.getBoolValue(feature)
                elif (feature.elementType == CAS_Type.TYPE_NAME_FLOAT):
                    return self.getFloatValue(feature)
                elif (feature.elementType == CAS_Type.TYPE_NAME_DOUBLE):    
                    return self.getFloatValue(feature)
                elif (feature.elementType == CAS_Type.TYPE_NAME_INTEGER):
                    return self.getIntValue(feature)
                elif (feature.elementType == CAS_Type.TYPE_NAME_LONG):
                    return self.getIntValue(feature)
                elif (feature.elementType == CAS_Type.TYPE_NAME_STRING):
                    return self.getStringValue(feature)
                elif type(feature.elementType) is TypeDescription:
                    return self.getFeatureValue(feature)
                else:
                    raise ValueError('feature type not recognized')
            #if feature has both element and range type        
            elif ((not feature.rangeType == None) and ( not feature.elementType == None)):
                #if rangeVal is not FSArray the combination is not valid and makes no sense, treat is as only rangeVal
                if ( not feature.rangeType.name == CAS_Type.TYPE_NAME_FSARRAY):
                    #if range type is primitive CAS type
                    if(feature.rangeType == CAS_Type.TYPE_NAME_BOOLEAN or feature.rangeType == CAS_Type.TYPE_NAME_FLOAT or 
                       feature.rangeType == CAS_Type.TYPE_NAME_DOUBLE or feature.rangeType == CAS_Type.TYPE_NAME_INTEGER or 
                       feature.rangeType == CAS_Type.TYPE_NAME_LONG or feature.rangeType == CAS_Type.TYPE_NAME_STRING):
                        return ' '.join(self.getListValue(feature))
                    #if its a FS        
                    elif type(feature.rangeType) is TypeDescription:
                        return self.getListValue(feature)
                    else:
                        raise ValueError('feature type not recognized')
                #if range type is FSArray, check element type
                else:
                    #if element type is CAS primitive
                    if(feature.elementType == CAS_Type.TYPE_NAME_BOOLEAN or feature.elementType == CAS_Type.TYPE_NAME_FLOAT or 
                       feature.elementType == CAS_Type.TYPE_NAME_DOUBLE or feature.elementType == CAS_Type.TYPE_NAME_INTEGER or 
                       feature.elementType == CAS_Type.TYPE_NAME_LONG or feature.elementType == CAS_Type.TYPE_NAME_STRING):
                        return ' '.join(self.getListValue(feature))    
                    elif type(feature.elementType) is TypeDescription:
                        return self.getListValue(feature)
                    else:
                        raise ValueError('feature type not recognized')
            #if feature has none element or range type    
            else:
                raise TypeError('range type or element type not found for feature',feature.name)        
    "override of default method from object class so that __getProperty can be called"    
    def __getattr__(self, attr):
        #these are the normal attributes of the class or super class , for them use object method
        if attr in ('_TOP__FSid','FSid','_TOP__featureValueDict','_TOP__featureIndex','_TOP__typeSystem',
                    'typeSystem','_TOP__CAS','CAS',
                    '_TOP__FStype','FStype'):
            
            return object.__getattr__(self, attr)
        #for other attributes call __getProperty , these are the feature names of FS
        else:
            return self.__getProperty(attr)
    "override of default method from object class so that __setProperty can be called"    
    def __setattr__(self, attr, value):
        #these are the normal attributes of the class or super class , for them use object method
        if attr in ('_TOP__FSid','FSid','_TOP__featureValueDict','_TOP__featureIndex','_TOP__typeSystem',
                    'typeSystem','_TOP__CAS','CAS',
                    '_TOP__FStype','FStype'):
            
            object.__setattr__(self, attr, value)
        #for other attributes call __getProperty , these are the feature names of FS    
        else:
            self.__setProperty(attr,value)        
    "adds the feature to featureIndex"
    "checks if type system supports this feature for this FS, otherwise throws exception"
    def __addToIndex(self,feature):
        if not type(feature) is Feature:
            raise TypeError(feature,'is not a Feature object')
            return      
        elif (feature.name == None):
            raise ValueError('feature does not have a name')
            return
        """
        else:
            #checks if type system supports this feature for this FS
            if not (feature.domain == self.FStype):
                raise AttributeError('feature is not supported in this FS')
        """
        for element in self.__featureIndex: #check if another feature with same name exists, override
            if(element.name == feature.name):
                self.RemoveFromIndex(feature)
                break
                "raise ValueError('feature exists in index')"
        self.__featureIndex.append(feature)
    "removes the feature to featureIndex and featureValueDict"
    def RemoveFromIndex(self,feature):
        if not type(feature) is Feature:
            raise TypeError(feature,'is not a Feature object')
        if (feature.name == None):
            raise ValueError('feature does not have a name')
        try:
            for element in self.__featureIndex:
                if(element.name == feature.name):
                    self.__featureIndex.remove(element)
            for element in self.__featureValueDict:
                if(element.get(feature.name) != None):
                    self.__featureValueDict.remove(element)
            
        except ValueError:
            raise ValueError('feature not in index')
    "Implementation of abstract method setValue of FeatureStructure,sets the value to featureValueDict, will be called from FeatureStructure setters"
    def setValue(self,feature,val):
        
        aFeature = {}
        
        "#if its a FS/list of FS or object/list of object will be saved"
        #if its a FSid/list of FSid it will be saved
        #if its a primitive type or list of primitive value,lit of value will be saved
                      
        #if val is FS list check if list items has a FSid
        if ((type(val) is list) and (type(feature.elementType) is TypeDescription)):
            for e in val:
                if (e.FSid == None):
                    raise ValueError('value is a FS, which does not have FSid')
                    return  
        #if val is FS check if it has a FSid    
        elif type(val) is TypeDescription:              
            if (val.FSid == None):
                raise ValueError('value is a FS, which does not have FSid')
                return

        aFeature[feature.name] = val                    
        self.__addToIndex(feature)
        self.__featureValueDict.append(aFeature)
    "Implementation of abstract method getValue of FeatureStructure,gets the value to featureValueDict, will be called from FeatureStructure getters"    
    def getValue(self,feature):
        if(feature.name == None):
            raise ValueError('feature does not have a name')
            return
        for element in self.__featureValueDict:
            if(element.get(feature.name) != None): #if its a FS or list of FS object, object list is returned                
                return element.get(feature.name)   #if its a primitive or list of primitive, value or value list is returned
    "Reurns all features"
    def getFeatures(self):
        return self.__featureIndex        
    "Reurns all features"
    def getFeatureValsAsDictList(self):
        return self.__featureValueDict        
    "Returns Fsid"    
    @property
    def FSid(self):
        return self.__FSid 
    "sets FSid"
    @FSid.setter    
    def FSid(self,val):
        self.__FSid = val
    "getter of parent property FStype"    
    @property
    def FStype(self):
        "return self.__FStype."
        return self.__FStype
    "Sets value of parent property FStype"
    @FStype.setter    
    def FStype(self,val):
        self.__FStype = val
    "getter of property typeSystemFilePath"    
    @property
    def typeSystem(self):
        return self.__typeSystem
    "Sets value of property typeSystemFilePath"
    @typeSystem.setter    
    def typeSystem(self,val):
        self.__typeSystem = val
    "getter of property CAS"    
    @property
    def CAS(self):
        return self.__CAS
    "Sets value of parent property CAS"
    @CAS.setter    
    def CAS(self,cas):
        self.__CAS = cas
