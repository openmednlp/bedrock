'''
Created on Jan 21, 2017

@author: Dibyojyoti
'''
from pycas.cas.core.TOP import TOP
from pycas.type.cas.Feature import Feature
from pycas.type.cas.CAS_Type import CAS_Type

class SofaFS(TOP):
    '''
    This class is a special class to represent sofa Feature structure 
    '''
    def __init__(self,FStype,FSid,typeSystem=None):
        '''
        Constructor
        '''
        #set the FSid
        TOP.__init__(self,FStype,FSid,typeSystem)

    def __setattr__(self, attr, value):
        if attr in ('sofaNum','sofaID','mimeType','sofaString'):
            object.__setattr__(self, attr, value)
        else:
            TOP.__setattr__(self, attr, value)
    def __getattr__(self, attr):
        if attr in ('sofaNum','sofaID','mimeType','sofaString'):
            return object.__getattr__(self, attr)
        else:
            return TOP.__getattr__(self, attr)

    "Returns sofaNum"
    @property
    def sofaNum(self):
        aFeature = Feature(self.FStype,'sofaNum')
        aFeature.description = ''
        aFeature.elementType =  CAS_Type.TYPE_NAME_INTEGER
        return self.getIntValue(aFeature)
    "Sets sofaNum"
    @sofaNum.setter
    def sofaNum(self, value):
        aFeature = Feature(self.FStype,'sofaNum')
        aFeature.description = ''
        aFeature.elementType =  CAS_Type.TYPE_NAME_INTEGER
        self.setIntValue(aFeature,value)
    "Returns sofaID"
    @property
    def sofaID(self):
        aFeature = Feature(self.FStype,'sofaID')
        aFeature.description = ''
        aFeature.elementType =  CAS_Type.TYPE_NAME_STRING
        return self.getStringValue(aFeature)
    "Sets sofaID"
    @sofaID.setter
    def sofaID(self, value):
        aFeature = Feature(self.FStype,'sofaID')
        aFeature.description = ''
        aFeature.elementType =  CAS_Type.TYPE_NAME_STRING
        self.setStringValue(aFeature,value)
    "Returns mimeType"
    @property
    def mimeType(self):
        aFeature = Feature(self.FStype,'mimeType')
        aFeature.description = ''
        aFeature.elementType =  CAS_Type.TYPE_NAME_STRING
        return self.getStringValue(aFeature)
    "Sets mimeType"
    @mimeType.setter
    def mimeType(self, value):
        aFeature = Feature(self.FStype,'mimeType')
        aFeature.description = ''
        aFeature.elementType =  CAS_Type.TYPE_NAME_STRING
        self.setStringValue(aFeature,value)
    "Returns sofaString"
    @property
    def sofaString(self):
        aFeature = Feature(self.FStype,'sofaString')
        aFeature.description = ''
        aFeature.elementType =  CAS_Type.TYPE_NAME_STRING
        return self.getStringValue(aFeature)
    "Sets sofaString"
    @sofaString.setter
    def sofaString(self, value):
        aFeature = Feature(self.FStype,'sofaString')
        aFeature.description = ''
        aFeature.elementType =  CAS_Type.TYPE_NAME_STRING
        self.setStringValue(aFeature,value)        