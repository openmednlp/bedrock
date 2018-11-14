'''
Created on Jan 27, 2017

@author: Dibyojyoti
'''
import os
import sys

class TypeSystem(object):
    '''
    This class represents the type system, and contains all the type descriptions with their features generated from typesystem xml
    '''
    def __init__(self):
        '''
        Constructor
        '''
        #name space property to represent the name space of the type system XML 
        self.namespace='' 
        #list of types(type descriptions)
        self.__typeDesc = []
    '''
    This method takes a tape description object and adds to the type description list
    '''    
    def addTypeDesc(self,typeDesc):
        self.__typeDesc.append(typeDesc)
    '''
    This methods returns the list of types(type descriptions)
    '''    
    def getAllTypeDesc(self):
        return self.__typeDesc
    '''
    This methods returns the type object which matches its name with the supplied type name as string, 
    if no matching type found returns None  
    '''
    def getType(self,name):
        typeDesc=None
        for td in self.__typeDesc:
            if td.name == name:
                typeDesc= td
                break
        return typeDesc
    '''
    This method returns the feature object for a given type name and feature name as supplied string
    if no feature found return None
    '''
    def getFeature(self,featureName,TypeDescName):
        tdesc= self.getType(TypeDescName)
        afeature = None
        if not (tdesc == None):
            #find the feature descriptions for the specified typeDesc
            afeature = tdesc.findFeatureByname(featureName)
            if(afeature == None and ( not tdesc.superType == None)):
                afeature = self.getFeature(featureName,tdesc.superType)
        return afeature
    '''
    This method removes the supplied type description object from the list of type descriptions 
    '''    
    def removeTypeDesc(self,typeDesc):
        for td in self.__typeDesc:
            if td.name == typeDesc.name:
                break
        self.__typeDesc.remove(td)
    "Returns namespace"
    @property
    def namespace(self):
        return self.__namespace
    "Sets the namespace of the type description"
    @namespace.setter
    def namespace(self, namespace):
        self.__namespace = namespace
    "writes type description into  a file- dependent on __toString method"    
    def write(self,filepath):
        tsstring = self.__toString()
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, "w") as f:
                f.write(tsstring)        
        except:
            print('Something went wrong! cannot create file',os.path.basename(filepath),'in',os.path.dirname(filepath))
            sys.exit(1)
    def __toString(self):
        "need to be developed"    