'''
Created on Jan 27, 2017

@author: Dibyojyoti
'''
from pycas.type.cas.TypeSystem import TypeSystem
from pycas.type.cas.TypeDescription import TypeDescription
from pycas.type.cas.Feature import Feature
from pycas.type.cas.CAS_Type import CAS_Type
from pycas.cas.parse.TypeSystemParser import TypeSystemParser

class TypeSystemFactory(object):
    '''
    This class takes a type system xml file path and generates a type system object containing all the type system
    information from the type system xml file
    '''


    def __init__(self):
        '''
        Constructor
        '''
    '''
    Creates and returns a TypeSytem object form a type system xml file.
    Args:
        typesystempath (Str):  path of a type system xml file.
    Returns:
        TypeSystem object
    '''
    def readTypeSystem(self,typesystempath):
        #create TypeSystem object
        typesystem = TypeSystem();
        #create TypeSystemParser object
        typesytemParser = TypeSystemParser()
        # set the type system path to TypeSystemParser
        typesytemParser.setTypeAsFile(typesystempath)
        # populate TypeSystem name space attribute to contain the base name space
        typesystem.namespace = typesytemParser.getTypeSystemDescNamespace()

        # iterate type description elements returned by the parser and create a typeDescription object for TypeSystem
        for tdelement in typesytemParser.getTypeDescElements():
            # create type description object
            TDname=typesytemParser.getElementText(typesytemParser.getTypeDescriptionName(tdelement))
            TDdesc=typesytemParser.getElementText(typesytemParser.getTypeDescriptionDescription(tdelement))
            typeDesc = TypeDescription(TDname,TDdesc)
            typeDesc.superType = typesytemParser.getElementText(typesytemParser.getTypeDescriptionSuperType(tdelement))
            #get the features element from parser
            features = typesytemParser.getTypeDescriptionFeatures(tdelement)
            if not features == None:
                #get the feature description element from the parser and create features object for typeDescription
                for felement in typesytemParser.getFeatureDescElements(features):
                    fdomain = TDname
                    fname = typesytemParser.getElementText(typesytemParser.getFeatureDescName(felement))
                    feature = Feature(fdomain,fname)
                    feature.description= typesytemParser.getElementText(typesytemParser.getFeatureDescDescription(felement))

                    rangeVal = typesytemParser.getFeatureDescRangeType(felement)
                    elementVal =  typesytemParser.getFeatureDescElementType(felement)
                    if(not rangeVal == None):
                        rangeValStr= typesytemParser.getElementText(rangeVal)
                        if(rangeValStr == CAS_Type.TYPE_NAME_FSARRAY and elementVal == None ):
                            raise TypeError(fname,'has only rangeType as FSArray, no element type found')
                            return
                        #if range type is primitive CAS type
                        if(rangeValStr == CAS_Type.TYPE_NAME_BOOLEAN or rangeValStr == CAS_Type.TYPE_NAME_FLOAT or
                           rangeValStr == CAS_Type.TYPE_NAME_DOUBLE or rangeValStr == CAS_Type.TYPE_NAME_INTEGER or
                           rangeValStr == CAS_Type.TYPE_NAME_LONG or rangeValStr == CAS_Type.TYPE_NAME_STRING):

                            #set the range type from type system of the feature
                            feature.rangeType = rangeValStr
                        else:
                            feature.rangeType = TypeDescription(rangeValStr)

                    if(not elementVal == None):
                        elementValStr = typesytemParser.getElementText(elementVal)
                        #if element type is primitive CAS type
                        if(elementValStr == CAS_Type.TYPE_NAME_BOOLEAN or elementValStr == CAS_Type.TYPE_NAME_FLOAT or
                           elementValStr == CAS_Type.TYPE_NAME_DOUBLE or elementValStr == CAS_Type.TYPE_NAME_INTEGER or
                           elementValStr == CAS_Type.TYPE_NAME_LONG or elementValStr == CAS_Type.TYPE_NAME_STRING):

                            #set the range type from type system of the feature
                            feature.elementType = elementValStr
                        else:
                            feature.elementType = TypeDescription(elementValStr)

                    #add the feature to the TypeDescription object
                    typeDesc.addFeature(feature)
            #add the TypeDescription to the TypeSystem object
            typesystem.addTypeDesc(typeDesc)

            #add inbuilt uima.cas.AnnotationBase type with sofa feature
            typeDescABase = TypeDescription('uima.cas.AnnotationBase','')
            typeDescABase.superType = 'uima.cas.TOP'
            featureSofa = Feature('uima.cas.AnnotationBase','sofa')
            featureSofa.description= ''
            featureSofa.elementType = TypeDescription('uima.cas.Sofa')
            typeDescABase.addFeature(featureSofa)
            typesystem.addTypeDesc(typeDescABase)

            #add inbuilt uima.tcas.Annotation type with begin  and end feature
            typeDescABase = TypeDescription('uima.tcas.Annotation','')
            typeDescABase.superType = 'uima.cas.AnnotationBase'
            #add begin feature to inbuilt uima.tcas.Annotation
            featureSofa = Feature('uima.tcas.Annotation','begin')
            featureSofa.description= ''
            featureSofa.elementType = CAS_Type.TYPE_NAME_INTEGER
            typeDescABase.addFeature(featureSofa)
            #add end feature to inbuilt uima.tcas.Annotation
            featureSofa = Feature('uima.tcas.Annotation','end')
            featureSofa.description= ''
            featureSofa.elementType = CAS_Type.TYPE_NAME_INTEGER
            typeDescABase.addFeature(featureSofa)
            #add inbuilt uima.tcas.Annotation type to the list of type descriptions
            typesystem.addTypeDesc(typeDescABase)

            #add inbuilt FSArray type
            typeDescFsArray = TypeDescription('uima.cas.FSArray','')
            typeDescFsArray.superType = 'uima.cas.TOP'
            typesystem.addTypeDesc(typeDescFsArray)

            #add inbuilt sofa type
            typeDescSofa = TypeDescription('uima.cas.Sofa','')
            typeDescSofa.superType = 'uima.cas.TOP'
            #add sofaNum feature to inbuilt sofa type
            featureSofaNum = Feature('uima.cas.Sofa','sofaNum')
            featureSofaNum.description= ''
            featureSofaNum.elementType = CAS_Type.TYPE_NAME_INTEGER
            typeDescSofa.addFeature(featureSofaNum)
            #add sofaID feature to inbuilt sofa type
            featureSofaID = Feature('uima.cas.Sofa','sofaID')
            featureSofaID.description= ''
            featureSofaID.elementType = CAS_Type.TYPE_NAME_STRING
            typeDescSofa.addFeature(featureSofaID)
            #add mimeType feature to inbuilt sofa type
            featureMimeType = Feature('uima.cas.Sofa','mimeType')
            featureMimeType.description= ''
            featureMimeType.elementType = CAS_Type.TYPE_NAME_STRING
            typeDescSofa.addFeature(featureMimeType)
            #add sofaString feature to inbuilt sofa type
            featureSofaString = Feature('uima.cas.Sofa','sofaString')
            featureSofaString.description= ''
            featureSofaString.elementType = CAS_Type.TYPE_NAME_STRING
            typeDescSofa.addFeature(featureSofaString)
            #add inbuilt sofa type to the list of type descriptions
            typesystem.addTypeDesc(typeDescSofa)

        return typesystem


    def readTypeSystemString(self,typesystemstring):
        #create TypeSystem object
        typesystem = TypeSystem();
        #create TypeSystemParser object
        typesytemParser = TypeSystemParser()
        # set the type system path to TypeSystemParser
        typesytemParser.setTypeAsString(typesystemstring)
        # populate TypeSystem name space attribute to contain the base name space
        typesystem.namespace = typesytemParser.getTypeSystemDescNamespace()

        # iterate type description elements returned by the parser and create a typeDescription object for TypeSystem
        for tdelement in typesytemParser.getTypeDescElements():
            # create type description object
            TDname=typesytemParser.getElementText(typesytemParser.getTypeDescriptionName(tdelement))
            TDdesc=typesytemParser.getElementText(typesytemParser.getTypeDescriptionDescription(tdelement))
            typeDesc = TypeDescription(TDname,TDdesc)
            typeDesc.superType = typesytemParser.getElementText(typesytemParser.getTypeDescriptionSuperType(tdelement))
            #get the features element from parser
            features = typesytemParser.getTypeDescriptionFeatures(tdelement)
            if not features == None:
                #get the feature description element from the parser and create features object for typeDescription
                for felement in typesytemParser.getFeatureDescElements(features):
                    fdomain = TDname
                    fname = typesytemParser.getElementText(typesytemParser.getFeatureDescName(felement))
                    feature = Feature(fdomain,fname)
                    feature.description= typesytemParser.getElementText(typesytemParser.getFeatureDescDescription(felement))

                    rangeVal = typesytemParser.getFeatureDescRangeType(felement)
                    elementVal =  typesytemParser.getFeatureDescElementType(felement)
                    if(not rangeVal == None):
                        rangeValStr= typesytemParser.getElementText(rangeVal)
                        if(rangeValStr == CAS_Type.TYPE_NAME_FSARRAY and elementVal == None ):
                            raise TypeError(fname,'has only rangeType as FSArray, no element type found')
                            return
                        #if range type is primitive CAS type
                        if(rangeValStr == CAS_Type.TYPE_NAME_BOOLEAN or rangeValStr == CAS_Type.TYPE_NAME_FLOAT or
                           rangeValStr == CAS_Type.TYPE_NAME_DOUBLE or rangeValStr == CAS_Type.TYPE_NAME_INTEGER or
                           rangeValStr == CAS_Type.TYPE_NAME_LONG or rangeValStr == CAS_Type.TYPE_NAME_STRING):

                            #set the range type from type system of the feature
                            feature.rangeType = rangeValStr
                        else:
                            feature.rangeType = TypeDescription(rangeValStr)

                    if(not elementVal == None):
                        elementValStr = typesytemParser.getElementText(elementVal)
                        #if element type is primitive CAS type
                        if(elementValStr == CAS_Type.TYPE_NAME_BOOLEAN or elementValStr == CAS_Type.TYPE_NAME_FLOAT or
                           elementValStr == CAS_Type.TYPE_NAME_DOUBLE or elementValStr == CAS_Type.TYPE_NAME_INTEGER or
                           elementValStr == CAS_Type.TYPE_NAME_LONG or elementValStr == CAS_Type.TYPE_NAME_STRING):

                            #set the range type from type system of the feature
                            feature.elementType = elementValStr
                        else:
                            feature.elementType = TypeDescription(elementValStr)

                    #add the feature to the TypeDescription object
                    typeDesc.addFeature(feature)
            #add the TypeDescription to the TypeSystem object
            typesystem.addTypeDesc(typeDesc)

            #add inbuilt uima.cas.AnnotationBase type with sofa feature
            typeDescABase = TypeDescription('uima.cas.AnnotationBase','')
            typeDescABase.superType = 'uima.cas.TOP'
            featureSofa = Feature('uima.cas.AnnotationBase','sofa')
            featureSofa.description= ''
            featureSofa.elementType = TypeDescription('uima.cas.Sofa')
            typeDescABase.addFeature(featureSofa)
            typesystem.addTypeDesc(typeDescABase)

            #add inbuilt uima.tcas.Annotation type with begin  and end feature
            typeDescABase = TypeDescription('uima.tcas.Annotation','')
            typeDescABase.superType = 'uima.cas.AnnotationBase'
            #add begin feature to inbuilt uima.tcas.Annotation
            featureSofa = Feature('uima.tcas.Annotation','begin')
            featureSofa.description= ''
            featureSofa.elementType = CAS_Type.TYPE_NAME_INTEGER
            typeDescABase.addFeature(featureSofa)
            #add end feature to inbuilt uima.tcas.Annotation
            featureSofa = Feature('uima.tcas.Annotation','end')
            featureSofa.description= ''
            featureSofa.elementType = CAS_Type.TYPE_NAME_INTEGER
            typeDescABase.addFeature(featureSofa)
            #add inbuilt uima.tcas.Annotation type to the list of type descriptions
            typesystem.addTypeDesc(typeDescABase)

            #add inbuilt FSArray type
            typeDescFsArray = TypeDescription('uima.cas.FSArray','')
            typeDescFsArray.superType = 'uima.cas.TOP'
            typesystem.addTypeDesc(typeDescFsArray)

            #add inbuilt sofa type
            typeDescSofa = TypeDescription('uima.cas.Sofa','')
            typeDescSofa.superType = 'uima.cas.TOP'
            #add sofaNum feature to inbuilt sofa type
            featureSofaNum = Feature('uima.cas.Sofa','sofaNum')
            featureSofaNum.description= ''
            featureSofaNum.elementType = CAS_Type.TYPE_NAME_INTEGER
            typeDescSofa.addFeature(featureSofaNum)
            #add sofaID feature to inbuilt sofa type
            featureSofaID = Feature('uima.cas.Sofa','sofaID')
            featureSofaID.description= ''
            featureSofaID.elementType = CAS_Type.TYPE_NAME_STRING
            typeDescSofa.addFeature(featureSofaID)
            #add mimeType feature to inbuilt sofa type
            featureMimeType = Feature('uima.cas.Sofa','mimeType')
            featureMimeType.description= ''
            featureMimeType.elementType = CAS_Type.TYPE_NAME_STRING
            typeDescSofa.addFeature(featureMimeType)
            #add sofaString feature to inbuilt sofa type
            featureSofaString = Feature('uima.cas.Sofa','sofaString')
            featureSofaString.description= ''
            featureSofaString.elementType = CAS_Type.TYPE_NAME_STRING
            typeDescSofa.addFeature(featureSofaString)
            #add inbuilt sofa type to the list of type descriptions
            typesystem.addTypeDesc(typeDescSofa)

        return typesystem
