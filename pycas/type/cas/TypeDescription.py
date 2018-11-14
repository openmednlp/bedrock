'''
Created on Jan 27, 2017

@author: Dibyojyoti
'''

class TypeDescription(object):
    '''
    This class represents a type(type description) object under a type system
    '''

    def __init__(self, name,desc=''):
        '''
        Constructor
        '''
        #name property
        self.name = name
        #description property
        self.description = desc
        #super type property
        self.superType=None
        #list of feature objects
        self.__features = []
    "Returns the name of the type description"                
    @property
    def name(self):
        return self.__name
    "Sets the name of the type description"
    @name.setter
    def name(self, name):
        self.__name = name
    "Returns the description of the type description"                
    @property
    def description(self):
        return self.__description
    "Sets the description of the type description"
    @description.setter
    def description(self, description):
        self.__description = description
    "Returns the superType of the type description"                
    @property
    def superType(self):
        return self.__superType
    "Sets the superType of the type description"
    @superType.setter
    def superType(self, superType):
        self.__superType = superType
    "add the given feature to the list of feature"    
    def addFeature(self,feature):
        self.__features.append(feature)
    "returns list of features under the type(type description)"    
    def getAllFeature(self):
        return self.__features
    "removes the given feature from the list of feature"
    def removeFeature(self,feature):
        for element in self.__features:
            if element.name == feature.name:
                break
        self.__features.remove(element)
    "finds and returns a feature from the list of features where name of the feature natches with the supplied string"
    "if no feature matches returns None"    
    def findFeatureByname(self,name):
        afeature=None
        for element in self.__features:
            if element.name == name:
                afeature = element
                break
        return afeature        