'''
Created on Dec 17, 2016

@author: Dibyojyoti
'''
from abc import ABC, abstractmethod
from pycas.type.cas.Feature import Feature
from pycas.type.cas.CAS_Type import CAS_Type 
from builtins import str
from pycas.type.cas.TypeDescription import TypeDescription

class FeatureStructure(ABC):
    '''
    This is an interface that provides contract which need to be developed to create feature structures
    '''
    @abstractmethod
    def __init__(self):
        '''
        Constructor
        '''
    "property type of feature structure,should be implemented by concrete child"    
    @property    
    @abstractmethod
    def FStype(self):
        pass
    "type setter,should be implemented by concrete child"
    @FStype.setter    
    @abstractmethod
    def FStype(self,val):
        pass
    "property cas that the FS belongs to,should be implemented by concrete child"    
    @property    
    @abstractmethod
    def CAS(self):
        pass
    "cas setter,should be implemented by concrete child"
    @CAS.setter    
    @abstractmethod
    def CAS(self,cas):
        pass
    
    "This method sets the value, will be called from inside all setters,"
    "Implementation should be given by child, its upto concrete child how to manage feature and value"    
    @abstractmethod
    def setValue(self,feature,val):
        pass
    "This method gets the value, will be called from inside all getters,"
    "Implementation should be given by child, its upto concrete child how to manage feature and value"    
    @abstractmethod
    def getValue(self,feature):
        pass    
    """
    Sets bool value to the feature,
    checks if val is bool, otherwise throws exception"
    checks if typesystem supports this type of value for this Feature, otherwise throws exception"
    Args:
        feature (Feature): feature to whom the value will be set.
        val (bool): bool value to be set to the feature.        
    """    
    def setBoolValue(self, feature, val):
        if not type(val) is bool:
            raise TypeError('value is not of type bool')
        elif not type(feature) is Feature:
            raise TypeError('feature is not a object of Feature')
        elif not (feature.elementType == CAS_Type.TYPE_NAME_BOOLEAN):
            raise TypeError('value is not acceptable for this Feature')
        else:
            self.setValue(feature,val)
    
    """
    Sets Integer value to the feature,
    checks if val is int, otherwise throws exception"
    checks if typesystem supports this type of value for this Feature, otherwise throws exception"
    Args:
        feature (Feature): feature to whom the value will be set.
        val (int): int value to be set to the feature.        
    """    
    def setIntValue(self, feature, val):
        if not type(val) is int:
            raise TypeError('value is not of type int')
        elif not type(feature) is Feature:
            raise TypeError('feature is not a object of Feature')
        elif not (feature.elementType == CAS_Type.TYPE_NAME_INTEGER):
            raise TypeError('value is not acceptable for this Feature')
        else:
            self.setValue(feature,val)
    """
    Sets Long value to the feature,
    checks if val is Long, otherwise throws exception"
    checks if typesystem supports this type of value for this Feature, otherwise throws exception"
    Args:
        feature (Feature): feature to whom the value will be set.
        val (long): long value to be set to the feature.
        
    """            
    def setLongValue(self, feature, val):
        "long and int same in python3"
        if not type(val) is int:
            raise TypeError('value is not of type long')
        elif not type(feature) is Feature:
            raise TypeError('feature is not a object of Feature')
        elif not (feature.elementType == CAS_Type.TYPE_NAME_LONG):
            raise TypeError('value is not acceptable for this Feature')
        else:
            self.setValue(feature,val)
    """
    Sets Float value to the feature,
    checks if val is float, otherwise throws exception"
    checks if typesystem supports this type of value for this Feature, otherwise throws exception"
    Args:
        feature (Feature): feature to whom the value will be set.
        val (float): float value to be set to the feature.
        
    """
    def setFloatValue(self, feature, val):
        if not type(val) is float:
            raise TypeError('value is not of type float')
        elif not type(feature) is Feature:
            raise TypeError('feature is not a object of Feature')
        elif not (feature.elementType == CAS_Type.TYPE_NAME_FLOAT):
            raise TypeError('value is not acceptable for this Feature')
        else:
            self.setValue(feature,val)        
    """
    Sets Complex value to the feature,
    checks if val is complex, otherwise throws exception"
    checks if typesystem supports this type of value for this Feature, otherwise throws exception"
    Args:
        feature (Feature): feature to whom the value will be set.
        val (complex): complex value to be set to the feature.
        
    """        
    def setComplexValue(self, feature, val):
        if not type(val) is complex:
            raise TypeError('value is not of type complex')
        elif not type(feature) is Feature:
            raise TypeError('feature is not a object of Feature')
        elif not (feature.elementType == CAS_Type.TYPE_NAME_STRING):
            "save complex as strig as cas does not support complex"
            raise TypeError('value is not acceptable for this Feature')
        else:
            self.setValue(feature,str(val))        
    """
    Sets List value to the feature,
    checks if list is a List, otherwise throws exception"
    checks if the elementType is supported for the list and whether each element in list is of type elementType, otherwise throws exception
    checks if typesystem supports this type of value for this Feature, otherwise throws exception"
    Args:
        feature (Feature): feature to whom the value will be set.
        elementType (CAS data Type): type of each element in list.
        list (List): list value to be set to the feature.        
    """
    def setListValue(self, feature, elementType, listval):
        if not type(listval) is list:
            raise TypeError('value is not of type list')
        elif not type(feature) is Feature:
            raise TypeError('feature is not a object of Feature')
        elif not ((feature.rangeType == elementType) or isinstance(feature.rangeType,TypeDescription)):
            raise TypeError('element type not supported by this feature')
        elif isinstance(elementType,TypeDescription):
            "if non primitive CAS type"
            for e in listval:                
                if not (isinstance(e,TypeDescription) and isinstance(e,FeatureStructure)):
                    raise TypeError('list value is not of type elementType')
                    break
        self.setValue(feature,listval)
    """
    Sets String value to the feature,
    checks if val is string, otherwise throws exception"
    checks if typesystem supports this type of value for this Feature, otherwise throws exception"
    Args:
        feature (Feature): feature to whom the value will be set.
        val (string): string value to be set to the feature.        
    """    
    def setStringValue(self, feature, val):
        if not type(val) is str:
            raise TypeError('value is not of type String')
        elif not type(feature) is Feature:
            raise TypeError('feature is not a object of Feature')
        if not (not feature.elementType==None and feature.elementType == CAS_Type.TYPE_NAME_STRING):
            raise TypeError('value is not acceptable for this Feature')
        else:
            self.setValue(feature,val)        
    """
    Sets value of type Feature to the feature,used for FS referencing, the id of the FS will be saved as value
    checks if val is of type Feature, otherwise throws exception"
    checks if typesystem supports this type of value for this Feature, otherwise throws exception"
    Args:
        feature (Feature): feature to whom the value will be set.
        val (Feature): Feature to be set as reference to the feature.
        
    """
    def setFeatureValue(self, feature, val):
        if not isinstance(val,FeatureStructure):
            raise TypeError('value is not of type Feature Structure')
        
        if ((not feature.elementType == None) and (not isinstance(feature.elementType,TypeDescription))):
            raise TypeError('element type of feature  is not of type TypeDescription')
        elif ((not feature.rangeType == None) and (not isinstance(feature.rangeType,TypeDescription))):
            raise TypeError('element type of feature  is not of type TypeDescription')

        if not type(feature) is Feature:
            raise TypeError('feature is not a object of Feature')
                
        """
        #expect Fsid of type int
        if not type(val) is int:
            raise TypeError('value is not acceptable for this Feature')
        """
        if ((not feature.elementType == None) and (not val.FStype.name == feature.elementType.name)):
            raise TypeError('value is not acceptable for this Feature')
        elif ((not feature.rangeType == None) and (not val.FStype.name == feature.rangeType.name)):
            raise TypeError('value is not acceptable for this Feature')
        self.setValue(feature,val)
    """
    Returns bool value of feature.
    checks if this Feature has value of type bool, otherwise throw exception"
    Args:
        feature (Feature): feature who's value will be returned.
    Returns:
        bool: The return value.
    """    
    def getBoolValue(self, feature):
        if not type(feature) is Feature:
            raise TypeError('feature is not a object of Feature')
        elif not (feature.elementType == CAS_Type.TYPE_NAME_BOOLEAN):
            raise TypeError('value is not acceptable for this Feature')
        else:
            return self.getValue(feature)
    """
    Returns int value of feature.
    checks if this Feature has value of type int, otherwise throw exception"
    Args:
        feature (Feature): feature who's value will be returned.
    Returns:
        Int: The return value.
    """    
    def getIntValue(self, feature):
        if not type(feature) is Feature:
            raise TypeError('feature is not a object of Feature')
        elif not (feature.elementType == CAS_Type.TYPE_NAME_INTEGER):
            raise TypeError('value is not acceptable for this Feature')
        else:
            return self.getValue(feature)
    """
    Returns Long value of feature.
    checks if this Feature has value of type long, otherwise throw exception"
    Args:
        feature (Feature): feature who's value will be returned.    
    Returns:
        Long: The return value.
    """            
    def getLongValue(self, feature):
        if not type(feature) is Feature:
            raise TypeError('feature is not a object of Feature')
        elif not (feature.elementType == CAS_Type.TYPE_NAME_LONG):
            raise TypeError('value is not acceptable for this Feature')
        else:
            return self.getValue(feature)
    """
    Returns Float value of feature.
    checks if this Feature has value of type Float, otherwise throw exception"
    Args:
        feature (Feature): feature who's value will be returned.    
    Returns:
        Float: The return value.
    """
    def getFloatValue(self, feature):
        if not type(feature) is Feature:
            raise TypeError('feature is not a object of Feature')
        elif not (feature.elementType == CAS_Type.TYPE_NAME_FLOAT):
            raise TypeError('value is not acceptable for this Feature')
        else:
            return self.getValue(feature)
    """
    Returns Complex value of feature.
    checks if this Feature has value of type complex, otherwise throw exception"
    Args:
        feature (Feature): feature who's value will be returned.    
    Returns:
        Complex: The return value.
    """
    def getComplexValue(self, feature):
        if not type(feature) is Feature:
            raise TypeError('feature is not a object of Feature')
        elif not (feature.elementType == CAS_Type.TYPE_NAME_STRING):
            raise TypeError('value is not acceptable for this Feature')
        else:
            return self.getValue(feature)
    """
    Returns List value of feature.
    checks if this Feature has value of type List, otherwise throw exception"
    Args:
        feature (Feature): feature who's value will be returned.    
    Returns:
        List: The return value.
    """
    def getListValue(self, feature):
        if not type(feature) is Feature:
            raise TypeError('feature is not a object of Feature')
        elif (feature.rangeType == None):
            raise TypeError('list value is not acceptable for this Feature')
        else:
            return self.getValue(feature)
    """
    Returns String value of feature.
    checks if this Feature has value of type string, otherwise throw exception"
    Args:
        feature (Feature): feature who's value will be returned.    
    Returns:
        String: The return value.
    """    
    def getStringValue(self, feature):
        if not type(feature) is Feature:
            raise TypeError('feature is not a object of Feature')
        elif not (feature.elementType == CAS_Type.TYPE_NAME_STRING):
            raise TypeError('value is not acceptable for this Feature')
        else:
            return self.getValue(feature)
    """
    Returns referenced Feature object of feature.
    checks if this Feature has value of type Feature, otherwise throw exception"
    Args:
        feature (Feature): feature who's value will be returned.    
    Returns:
        Feature: The return value.
    """    
    def getFeatureValue(self, feature):
        if not type(feature) is Feature:
            raise TypeError('feature is not a object of Feature')
        elif ((not feature.elementType == None) and   (not isinstance(feature.elementType,TypeDescription))):
            raise TypeError('value is not acceptable for this Feature')
        elif ((not feature.rangeType == None ) and (not isinstance(feature.rangeType,TypeDescription))):
            raise TypeError('value is not acceptable for this Feature')
        else:
            return self.getValue(feature)