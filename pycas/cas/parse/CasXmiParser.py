'''
Created on Dec 12, 2016

@author: Dibyojyoti
'''
from lxml import etree
import os
import sys
class CasXmiParser(object):
    '''
    Class to parse and access parts of CAS Xmi
    '''
    def __init__(self):
        '''
        Constructor
        '''
    "Sets Xmi as String"    
    def setXmiAsString(self,xmi):
        self.Xmi = xmi
        self.root = etree.XML(self.Xmi.encode('utf-8'))
    "Sets Xmi as filepath"    
    def setXmiAsFile(self,filepath):        
        self.Xmi = etree.tostring(etree.parse(filepath).getroot())
        self.root = etree.XML(self.Xmi)
    "Returns Xmi as String"
    def getXmiAsString(self):
            return self.Xmi
    "writes Xmi to a give filepath"    
    def witeXmiAsFile(self,filename):
        try:
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename, "w") as f:
                f.write(self.Xmi.decode("utf-8"))        
        except:
            print('Something went wrong! cannot create file',os.path.basename(filename),'in',os.path.dirname(filename))
            sys.exit(1)
    "Returns Xmi element  as lxml Element"                         
    def getRootElement(self):
        return self.root
    "Returns Xmi element  as String"
    def getRootElementAsString(self):
        return etree.tostring(self.root).decode("utf-8")
    "Returns Xmi element's tag and namespace as dictionary"    
    def getRootTagAsDict(self):
        dictelem = {}
        dictelem[etree.QName(self.root.tag).localname] = etree.QName(self.root.tag).namespace
        return dictelem
    "Returns Xmi element's attribute names as list"
    def getRootAttribteNames(self):
        return sorted(self.root.keys())
    "Returns Xmi element's attribute names and values as list"
    def getRootAttributesAsList(self):
        return sorted(self.root.items())
    "Returns Xmi element's attribute names and values as dictionary"  
    def getRootAttributesAsDict(self):
        return dict(self.root.attrib)
    "Returns cas:Null element as lxml Element"
    def getCasNullChild(self):
        return self.root.find('{*}NULL')
    "Returns cas:Sofa element as lxml Element"
    def getCasSofaChild(self):
        return self.root.find('{*}Sofa')
    "Returns cas:View element as lxml Element"
    def getCasViewChild(self):
        return self.root.find('{*}View')
    "Returns All cas: element as list of lxml Element"
    def getCasChildren(self):
        casElement = []
        for e in self.root.iter('{*}NULL','{*}Sofa','{*}View'):
            casElement.append(e)
        return casElement
    "Returns All cas: element as List of String"
    def getCasChildrenAsString(self):
        casElement = []
        for e in self.root.iter('{*}NULL','{*}Sofa','{*}View'):
            casElement.append(etree.tostring(e).decode("utf-8"))
        return casElement
    "Returns non cas: element as list of lxml Element"
    def getNonCasChildren(self):
        nonCasElement = []
        exmi = self.root.find('{*}XMI')
        ecasnull = self.root.find('{*}NULL')
        ecassofa = self.root.find('{*}Sofa')
        ecasview = self.root.find('{*}View')
        for e in self.root.iter():
            if(e not in (exmi,ecasnull,ecassofa,ecasview)):
                nonCasElement.append(e)    
        return nonCasElement
    "Returns non cas: element as list of String"
    def getNonCasChildrenAsString(self):
        nonCasElement = []
        exmi = self.root.find('{*}XMI')
        ecasnull = self.root.find('{*}NULL')
        ecassofa = self.root.find('{*}Sofa')
        ecasview = self.root.find('{*}View')
        for e in self.root.iter():
            if(e not in (exmi,ecasnull,ecassofa,ecasview)):
                nonCasElement.append(etree.tostring(e).decode("utf-8"))    
        return nonCasElement
    "converts a Xmi child element to string, contain extra namespace mappings specified in root element"                  
    def convertChildToString(self,child):
        return etree.tostring(child, pretty_print=True).decode("utf-8")
    "Returns the first element as lxml Element with matching tag"
    def findChildByTag(self,tagString):
        return self.root.find(tagString)
    "Returns the first element as lxml Element with matching localname"
    def findChildByLocalname(self,localnameString):
        return self.root.find('{*}'+localnameString)
    "Returns the first element as lxml Element with matching namespace"
    def findChildByNamespace(self,namespaceString):
        return self.root.find('{'+namespaceString+'}*')
    "Returns all the elements as lxml Element with matching tag"
    def findChildrenByTag(self,tagString):
        return self.root.findall(tagString)
    "Returns all the elements as lxml Element with matching localname"
    def findChildrenByLocalname(self,localnameString):
        return self.root.findall('{*}'+localnameString)
    "Returns all the elements as lxml Element with matching namespace"
    def findChildrenByNamespace(self,namespaceString):
        return self.root.findall('{'+namespaceString+'}*')
    "Returns the first element as lxml Element with matching attribute name"
    def findChildByAttribute(self,attrb):
        return self.root.find('.//*[@'+attrb+']')
    "Returns all the elements as lxml Element with matching attribute name"
    def findChildrenByAttribute(self,attrb):
        return self.root.findall('.//*[@'+attrb+']')
    "Returns the given child element tag as dictionary"    
    def getChildTagAsDict(self,child):
        dictelem = {}
        dictelem[etree.QName(child.tag).localname] = etree.QName(child.tag).namespace
        return dictelem
    "Returns all child element tags as list"
    def getChildNamesAsList(self):
        elementlist = []
        for child in self.root:
            elementlist.append(child.tag)
        return elementlist
    "Returns the attribute names of given child"        
    def getChildAttribteNames(self,child):
        return sorted(child.keys())
    "Returns the attribute names and values as list of given child"
    def getChildAttributesAsList(self,child):
        return sorted(child.items())
    "Returns the attribute names and values as dictionary of given child"
    def getChildAttributesAsDict(self,child):
        return dict(child.attrib)
    "Returns index of given child in xmi"
    def getChildIndex(self,child):
        return self.root.index(child)
    "Returns true if the element has a name space"
    def hasNamespace(self,element):
        if(etree.QName(element).namespace !=None):
            return True
        else:
            return False
    "Returns the namespace of an element"    
    def getNamespace(self,element):
        return etree.QName(element).namespace
    "Returns the localname of an element"
    def getLocalname(self,element):
        return etree.QName(element).localname
    "Returns the tagname with namespace  of an element"
    def getTag(self,element):
        return element.tag
    "Returns list of child tags filtered by tagname"
    def getChildTagsFilterBytag(self,tag):
        elements = []
        for child in self.root.iter(tag):
            elements.append(child.tag);
        return elements    
    
