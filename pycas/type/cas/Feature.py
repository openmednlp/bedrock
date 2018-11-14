'''
Created on Dec 17, 2016

@author: Dibyojyoti
'''
from pycas.type.cas.CAS_Type import CAS_Type
from pycas.type.cas.TypeDescription import TypeDescription
class Feature(object):
    '''
    This class represents a feature element in type system and a property of a FeatureStructure
    '''
    def __init__(self, domain,name):
        '''
        Constructor
        '''
        #domain in the name of the type description under which the feature is listed
        self.domain = domain
        #name of the feature
        self.name   = name
        #description of the feature
        self.__description = None
        #range type and element type of the feature, both can not be empty
        self.__rangeType = None
        self.__elementType = None
    "Returns the domain name which is the name of the type description under which the feature is defined"    
    @property
    def domain(self):
        return self.__domain
    "Sets the domain name of the feature"
    @domain.setter
    def domain(self, domain):
        self.__domain = domain
    "Returns the name of the feature"                
    @property
    def name(self):
        return self.__name
    "Sets the name of the feature"
    @name.setter
    def name(self, name):
        self.__name = name
    "Returns the description of the feature"    
    @property
    def description(self):
        return self.__description
    "sets the description of the feature"
    @description.setter
    def description(self, description):
        self.__description = description
    "Returns the rangeType of the feature"
    @property
    def rangeType(self):
        return self.__rangeType
    "Sets the rangeType of the feature, checks if the value is of primitive CAS_type or a type object, throws exception otherwise"
    @rangeType.setter
    def rangeType(self, rangeType):
        if not  (  rangeType == CAS_Type.TYPE_NAME_BOOLEAN or rangeType == CAS_Type.TYPE_NAME_FLOAT
                 or rangeType == CAS_Type.TYPE_NAME_INTEGER or rangeType == CAS_Type.TYPE_NAME_LONG
                 or rangeType == CAS_Type.TYPE_NAME_STRING or rangeType == CAS_Type.TYPE_NAME_FSARRAY
                 or rangeType == CAS_Type.TYPE_NAME_DOUBLE or isinstance(rangeType,TypeDescription)):
            raise TypeError('value is not of type primitive CAS Type or a type object')
        else:
            self.__rangeType = rangeType            
    "Return the elementType of the feature"
    @property
    def elementType(self):
        return self.__elementType
    "Sets the elementType of the feature, checks if the value is of primitive CAS_type or a type object, throws exception otherwise"
    @elementType.setter
    def elementType(self, elementType):
        if not  (  elementType == CAS_Type.TYPE_NAME_BOOLEAN or elementType == CAS_Type.TYPE_NAME_FLOAT
             or elementType == CAS_Type.TYPE_NAME_INTEGER or elementType == CAS_Type.TYPE_NAME_LONG
             or elementType == CAS_Type.TYPE_NAME_STRING or elementType == CAS_Type.TYPE_NAME_FSARRAY
             or elementType == CAS_Type.TYPE_NAME_DOUBLE or isinstance(elementType,TypeDescription)):
            raise TypeError('value is not of type primitive CAS Type or a type object')
        else:
            self.__elementType = elementType 