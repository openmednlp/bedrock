'''
Created on Dec 17, 2016

@author: Dibyojyoti
'''
from pycas.cas.core.TOP import TOP

class AnnotationBase(TOP):
    '''
    This class represents a base class of all annotations
    Its a subclass of TOP
    Params:
        FStype (typeDescription) : type of the annotation
        FSid (int) : id of the annotation
        typeSystem (TypeSystem) : type system object 
    '''
    def __init__(self,FStype,FSid,typeSystem):
        '''
        Constructor
        '''
        #set the FSid
        TOP.__init__(self,FStype,FSid,typeSystem)

    @property
    def view(self):
        return self.CAS.getSofaCasView()
