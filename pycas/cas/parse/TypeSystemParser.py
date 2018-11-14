'''
Created on Dec 12, 2016

@author: Dibyojyoti
'''
from lxml import etree
import os
import sys

class TypeSystemParser(object):
    '''
    This class parses a type system XML file
    '''
    def __init__(self):
        '''
        Constructor
        '''        
    """    
    def __init__(self, filepath):
        '''
        Constructor
        '''
        self.typeStringRoot = etree.XML(etree.tostring(etree.parse(filepath).getroot()))
    """
    "Sets typesystem as string"        
    def setTypeAsString(self,typeString):
        self.typeStringRoot = etree.XML(typeString.encode('utf-8'))
    "Sets typesystem as filepath"    
    def setTypeAsFile(self,filepath):        
        self.typeStringRoot = etree.XML(etree.tostring(etree.parse(filepath).getroot()))
    "Gets typesystem as string"    
    def getTypeAsString(self):
        return etree.tostring(self.typeStringRoot).decode("utf-8")
    "Writes typesystem as xml file"
    def witeTypeAsFile(self,filename):
        string = '<?xml version="1.0" encoding="UTF-8"?>'+etree.tostring(self.typeStringRoot).decode("utf-8")
        try:
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename, "w") as f:
                f.write(string)        
        except:
            print('Something went wrong! cannot create file',os.path.basename(filename),'in',os.path.dirname(filename))
            sys.exit(1)
    "Gets typesystem root element as lxml Element"                                 
    def getTypeSystemRoot(self):
        return self.typeStringRoot
    "Gets typesystem root element as String"
    def getTypeSystemRootAsString(self):
        return etree.tostring(self.typeStringRoot).decode("utf-8")
    "Gets typesystem description tag name with namespace"    
    def getTypeSystemDesc(self):
        return self.typeStringRoot.tag
    "Gets typesystem description tag namespace"
    def getTypeSystemDescNamespace(self):
        return etree.QName(self.typeStringRoot.tag).namespace
    "Gets typesystem description tag name"
    def getTypeSystemDescLocalname(self):
        return etree.QName(self.typeStringRoot.tag).localname
    "Gets typesystem types as lxml Element"    
    def getTypeSystemTypes(self):
        return self.typeStringRoot[0]
    "Gets typesystem types element as String"
    def getTypeSystemTypesAsString(self):
        return etree.tostring(self.typeStringRoot[0]).decode("utf-8")
    "Gets typesystem type description elements as list of lxml Element"    
    def getTypeDescElements(self):
        elements = []
        for child in self.typeStringRoot[0].iter('{*}typeDescription'):
            elements.append(child);
        return elements
    "finds typesystem's type description element as lxml Element by type description name"    
    def findTypeDescElementByName(self,typeDescName):
        tdesc = None
        for child in self.typeStringRoot[0].iter('{*}typeDescription'):
            if (self.getTypeDescriptionName(child).text == typeDescName):
                tdesc = child;
                break;
        return tdesc
    "finds typesystem's feature in a type description elements as list of lxml Element by type description name"    
    def findTypeDescFeatureByName(self,featureName,typeDescName):
        tdesc= self.findTypeDescElementByName(typeDescName)
        
        afeature = None
        """
        if(tdesc == None):
            raise ValueError(typeDescName,'does not exists in type system')
            return
        """    
        if not (tdesc == None):
            #get the feature descriptions list for the specified typeDesc
            tdfeatures= self.getTypeDescriptionFeatures(tdesc)
            if not (tdfeatures == None):
                featureDescs = self.getFeatureDescElements(tdfeatures)
                for fdscelem in featureDescs:
                    if(self.getFeatureDescName(fdscelem).text == featureName):
                        afeature= fdscelem
                        break    
            #If matching feature not found, and super type exists for the type description, search in super type
            if(afeature == None and ( not self.getTypeDescriptionSuperType(tdesc) == None)):
                afeature = self.findTypeDescFeatureByName(featureName,self.getTypeDescriptionSuperType(tdesc).text)  
        return afeature
    "Gets typesystem type description elements as list of String"
    def getTypeDescElementsAsStingList(self):
        elements = []
        for child in self.typeStringRoot[0].iter('{*}typeDescription'):
            elements.append(etree.tostring(child).decode("utf-8").replace('\n','').replace('\t','').replace('  ',''));
        return elements
    "Gets typesystem type description name element as lxml Element from a given typesystem description"
    def getTypeDescriptionName(self,typeDescriptionElement):
        tdname = None
        for e in typeDescriptionElement:
            if(self.getElementLocalname(e) == 'name'):
                tdname = e
                break
            else:
                continue
        return tdname        
        "return typeDescriptionElement[0]"
    "Gets typesystem type description name element as String from a given typesystem description"    
    def getTypeDescriptionNameAsString(self,typeDescriptionElement):
        tdn = self.getTypeDescriptionName(typeDescriptionElement)
        if tdn is None:
            return ""
        else:
            return etree.tostring(tdn).decode("utf-8").replace('\n','').replace('\t','').replace('  ','')
    "Gets typesystem type description description element as lxml Element from a given typesystem description"    
    def getTypeDescriptionDescription(self,typeDescriptionElement):
        tddesc = None
        for e in typeDescriptionElement:
            if(self.getElementLocalname(e) == 'description'):
                tddesc = e
                break
            else:
                continue
        return tddesc
        "return typeDescriptionElement[1]"
    "Gets typesystem type description description element as String from a given typesystem description"    
    def getTypeDescriptionDescriptionAsString(self,typeDescriptionElement):
        tdd = self.getTypeDescriptionDescription(typeDescriptionElement)
        if tdd is None:
            return ""
        else:
            return etree.tostring(tdd).decode("utf-8").replace('\n','').replace('\t','').replace('  ','')
    "Gets typesystem type description supertype element as lxml Element from a given typesystem description"    
    def getTypeDescriptionSuperType(self,typeDescriptionElement):
        tdsutype = None
        for e in typeDescriptionElement:
            if(self.getElementLocalname(e) == 'supertypeName'):
                tdsutype = e
                break
            else:
                continue
        return tdsutype
        "return typeDescriptionElement[2]"
    "Gets typesystem type description supertype element as String from a given typesystem description"    
    def getTypeDescriptionSuperTypeAsString(self,typeDescriptionElement):
        tds = self.getTypeDescriptionSuperType(typeDescriptionElement)
        if tds is None:
            return ""
        else:
            return etree.tostring(tds).decode("utf-8").replace('\n','').replace('\t','').replace('  ','')
    "feature tag may not exists"
    "Gets typesystem type description features element as lxml Element from a given typesystem description"        
    def getTypeDescriptionFeatures(self,typeDescriptionElement):
        tdsutype = None
        for e in typeDescriptionElement:
            if(self.getElementLocalname(e) == 'features'):
                tdsutype = e
                break
            else:
                continue
        return tdsutype
        """
        if(len(typeDescriptionElement) == 4):
            return typeDescriptionElement[3]
        else: 
            return None
        """
    "Gets typesystem type description features element as String from a given typesystem description"    
    def getTypeDescriptionFeaturesAsString(self,typeDescriptionElement):
        tdf = self.getTypeDescriptionFeatures(typeDescriptionElement)
        if tdf is None:
            return ""
        else:
            return etree.tostring(tdf).decode("utf-8")
    "Gets feature description elements as list of lxml Element from a given features element"    
    def getFeatureDescElements(self,features):
        featureDescElements = []
        for child in features.iter('{*}featureDescription'):
            featureDescElements.append(child);
        return featureDescElements
    "Gets feature description elements as list of String from a given features element"
    def getFeatureDescElementsAsStingList(self,features):
        featureDescElements = []
        for child in features.iter('{*}featureDescription'):
            featureDescElements.append(etree.tostring(child).decode("utf-8").replace('\n','').replace('\t','').replace('  ',''));
        return featureDescElements
    "Gets feature description's name elements as lxml Element from a given features element"
    def getFeatureDescName(self,featureDesc):
        fdescname = None
        for e in featureDesc:
            if(self.getElementLocalname(e) == 'name'):
                fdescname = e
                break
            else:
                continue
        return fdescname
    "Gets feature description's description elements as lxml Element from a given features element"    
    def getFeatureDescDescription(self,featureDesc):
        fdescdesc = None
        for e in featureDesc:
            if(self.getElementLocalname(e) == 'description'):
                fdescdesc = e
                break
            else:
                continue
        return fdescdesc
    "Gets feature description's rangetype elements as lxml Element from a given features element"        
    def getFeatureDescRangeType(self,featureDesc):
        fdescrtype = None
        for e in featureDesc:
            if(self.getElementLocalname(e) == 'rangeTypeName'):
                fdescrtype = e
                break
            else:
                continue
        return fdescrtype
    "Gets feature description's elementtype elements as lxml Element from a given features element"            
    def getFeatureDescElementType(self,featureDesc):
        fdescetype = None
        for e in featureDesc:
            if(self.getElementLocalname(e) == 'elementType'):
                fdescetype = e
                break
            else:
                continue
        return fdescetype
    "Gets feature description's name elements as String from a given features element"                
    def getFeatureDescNameAsString(self,featureDesc):
        tdfdn = self.getFeatureDescName(featureDesc)
        if tdfdn is None:
            return ""
        else:
            return etree.tostring(tdfdn).decode("utf-8").replace('\n','').replace('\t','').replace('  ','')
    "Gets feature description's description elements as String from a given features element"        
    def getFeatureDescDescriptionAsString(self,featureDesc):
        tdfdd = self.getFeatureDescDescription(featureDesc)
        if tdfdd is None:
            return ""
        else:
            return etree.tostring(tdfdd).decode("utf-8").replace('\n','').replace('\t','').replace('  ','')
    "Gets feature description's rangetype elements as String from a given features element"            
    def getFeatureDescRangeTypeAsString(self,featureDesc):
        tdfdr = self.getFeatureDescRangeType(featureDesc)
        if tdfdr is None:
            return ""
        else:
            return etree.tostring(tdfdr).decode("utf-8").replace('\n','').replace('\t','').replace('  ','')
    "Gets feature description's elementtype elements as String from a given features element"                
    def getFeatureDescElementTypeAsString(self,featureDesc):
        tdfde = self.getFeatureDescElementType(featureDesc)
        if tdfde is None:
            return ""
        else:
            return etree.tostring(tdfde).decode("utf-8").replace('\n','').replace('\t','').replace('  ','')
    "Gets tag name with namespace as String from a given lxml element"                 
    def getElementTag(self,element):
        return element.tag
    "Gets text as String from a given lxml element"
    def getElementText(self,element):
        return element.text
    "Gets tag namespace as String from a given lxml element"    
    def getElementNamespace(self,element):
        return etree.QName(element.tag).namespace
    "Gets tag name as String from a given lxml element"
    def getElementLocalname(self,element):
        return etree.QName(element.tag).localname    