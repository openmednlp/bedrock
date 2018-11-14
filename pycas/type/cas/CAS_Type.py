'''
Created on Dec 17, 2016

@author: Dibyojyoti
'''
from abc import ABC, abstractmethod

class CAS_Type(ABC):
    '''
    This class holds the uima.cas basic data types named as string will be used to check cas primitive types of a feature
   '''    
    "TOP type"
    TYPE_NAME_TOP = "uima.cas.TOP";
    "Integer type"
    TYPE_NAME_INTEGER = "uima.cas.Integer";
    "Float type"
    TYPE_NAME_FLOAT = "uima.cas.Float";
    "String type"
    TYPE_NAME_STRING = "uima.cas.String";
    "Boolean type"
    TYPE_NAME_BOOLEAN = "uima.cas.Boolean";
    "Byte type"
    TYPE_NAME_BYTE = "uima.cas.Byte";
    "Short type"
    TYPE_NAME_SHORT = "uima.cas.Short";
    "Long type"
    TYPE_NAME_LONG = "uima.cas.Long";
    "Double type"
    TYPE_NAME_DOUBLE = "uima.cas.Double";
    "FSARRAY type"
    TYPE_NAME_FSARRAY = "uima.cas.FSArray";
    @abstractmethod    
    def __init__(self):
        '''
        Constructor
        '''