'''
Created on Dec 17, 2016

@author: Dibyojyoti
'''
from pycas.cas.core.AnotationBase import AnnotationBase

class Annotation(AnnotationBase):
    '''
    This class represents a base class for text annotation
    uses parent AnnotationBase properties
    Params:
        FStype (TypeDescription) : type of the annotation
        FSid(int): id of FS
        typeSystem (TypeSystem) : type system object
    '''
    def __init__(self,FStype,FSid,typeSystem):
        '''
        Constructor
        '''
        #set type, id and type system
        AnnotationBase.__init__(self,FStype,FSid,typeSystem)
    "returns the covered text by this annoation FS"
    def getCoveredText(self):
        if not self.CAS == None:
            return self.CAS.documentText[self.begin:self.end]
        else:
            raise ValueError('CAS is not set for the feature structure')
