
'''
Created on Dec 14, 2016

@author: Dibyojyoti
unit test cases to check TypeSystemParser functionality
'''
import unittest2 as unittest
from pycas.cas.parse.TypeSystemParser import TypeSystemParser

class TestTypeSystemParserMethods(unittest.TestCase):
    def test_witeTypeAsFile(self):
        castypesytem = TypeSystemParser()
        castypesytem.setTypeAsFile('tests/testing_data/typesystem.xml')
        #provide proper path
        "self.assertEqual(castypesytem.witeTypeAsFile('C:/Users/Dibyojyoti/Desktop/scriptop/typesystem_op.xml'), None)"

    def test_type(self):
        castypesytem = TypeSystemParser()
        castypesytem.setTypeAsFile('tests/testing_data/typesystem.xml')
        self.assertEqual(type(castypesytem), TypeSystemParser );
        self.assertEqual(isinstance(castypesytem,TypeSystemParser), True );
        self.assertEqual(issubclass(type(castypesytem),str), False );

    def test_getTypeSystemRootAsString(self):
        castypesytem = TypeSystemParser()
        castypesytem.setTypeAsFile('tests/testing_data/typesystem.xml')
        "print(castypesytem.getTypeSystemRoot())"
        self.assertEqual(castypesytem.getTypeSystemRootAsString(), castypesytem.getTypeAsString() );

    def test_getTypeSystem(self):
        castypesytem = TypeSystemParser()
        castypesytem.setTypeAsFile('tests/testing_data/typesystem.xml')

        self.assertEqual(castypesytem.getTypeSystemDesc(), '{http://uima.apache.org/resourceSpecifier}typeSystemDescription')
        self.assertEqual(castypesytem.getTypeSystemDescNamespace(),'http://uima.apache.org/resourceSpecifier')
        self.assertEqual(castypesytem.getTypeSystemDescLocalname(),'typeSystemDescription')
        "print(castypesytem.getTypeSystemTypes())"
        "print(castypesytem.getTypeSystemTypesAsString())"

    def test_getTypeDesc(self):
        castypesytem = TypeSystemParser()
        castypesytem.setTypeAsFile('tests/testing_data/typesystem.xml')
        "print(castypesytem.getTypeDescElements())"
        "print(castypesytem.getTypeDescElements()[0])"
        self.assertEqual(castypesytem.getTypeDescElementsAsStingList()[0],
        '<typeDescription xmlns="http://uima.apache.org/resourceSpecifier"><name>uima.tcas.DocumentAnnotation</name><description/><supertypeName>uima.tcas.Annotation</supertypeName><features><featureDescription><name>language</name><description/><rangeTypeName>uima.cas.String</rangeTypeName></featureDescription></features></typeDescription>')
        self.assertEqual(castypesytem.getElementTag(castypesytem.getTypeDescElements()[0]),
                         '{http://uima.apache.org/resourceSpecifier}typeDescription')
        self.assertEqual(castypesytem.getElementNamespace(castypesytem.getTypeDescElements()[0]),
                         'http://uima.apache.org/resourceSpecifier')
        self.assertEqual(castypesytem.getElementLocalname(castypesytem.getTypeDescElements()[0]),'typeDescription')
        self.assertEqual(castypesytem.getElementText(castypesytem.getTypeDescElements()[0]), '\n            ')

    def test_getTypeDescriptionName(self):
        castypesytem = TypeSystemParser()
        castypesytem.setTypeAsFile('tests/testing_data/typesystem.xml')
        "print(castypesytem.getTypeDescriptionName(castypesytem.getTypeDescElements()[0]))"
        self.assertEqual(castypesytem.getElementText(castypesytem.getTypeDescriptionName(castypesytem.getTypeDescElements()[0])),
              'uima.tcas.DocumentAnnotation')

    def test_getTypeDescriptionDescription(self):
        castypesytem = TypeSystemParser()
        castypesytem.setTypeAsFile('tests/testing_data/typesystem.xml')
        "print(castypesytem.getTypeDescriptionDescription(castypesytem.getTypeDescElements()[0]))"

    def test_getTypeDescriptionSuperType(self):
        castypesytem = TypeSystemParser()
        castypesytem.setTypeAsFile('tests/testing_data/typesystem.xml')
        self.assertEqual(castypesytem.getElementTag(castypesytem.getTypeDescriptionSuperType(castypesytem.getTypeDescElements()[0])),
                         '{http://uima.apache.org/resourceSpecifier}supertypeName')
        self.assertEqual(castypesytem.getElementText(castypesytem.getTypeDescriptionSuperType(castypesytem.getTypeDescElements()[0])),
                         'uima.tcas.Annotation')

    def test_getTypeDescriptionFeatures(self):
        castypesytem = TypeSystemParser()
        castypesytem.setTypeAsFile('tests/testing_data/typesystem.xml')
        "print(castypesytem.getTypeDescriptionFeatures(castypesytem.getTypeDescElements()[0]))"
        self.assertEqual(castypesytem.getElementTag(castypesytem.getTypeDescriptionFeatures(castypesytem.getTypeDescElements()[0])),
                         '{http://uima.apache.org/resourceSpecifier}features')
        """how to iterate type description elements
        for child in castypesytem.getTypeDescElements():
            print(castypesytem.getElementText(castypesytem.getTypeDescriptionName(child)))
            print(castypesytem.getElementTag(castypesytem.getTypeDescriptionDescription(child)))
            print(castypesytem.getElementTag(castypesytem.getTypeDescriptionSuperType(child)))
            print(castypesytem.getTypeDescriptionFeatures(child))
            print(' ')
        """

    def test_getTypeDescriptionXXXAsString(self):
        castypesytem = TypeSystemParser()
        castypesytem.setTypeAsFile('tests/testing_data/typesystem.xml')
        typeDescElem = castypesytem.getTypeDescElements()[0]
        self.assertEqual(castypesytem.getTypeDescriptionNameAsString(typeDescElem),
              '<name xmlns="http://uima.apache.org/resourceSpecifier">uima.tcas.DocumentAnnotation</name>')
        self.assertEqual(castypesytem.getTypeDescriptionDescriptionAsString(typeDescElem),
              '<description xmlns="http://uima.apache.org/resourceSpecifier"/>')
        self.assertEqual(castypesytem.getTypeDescriptionSuperTypeAsString(typeDescElem),
              '<supertypeName xmlns="http://uima.apache.org/resourceSpecifier">uima.tcas.Annotation</supertypeName>')

        """how to iterate type description elements
        for child in castypesytem.getTypeDescElements():
            print(castypesytem.getTypeDescriptionNameAsString(child))
            print(castypesytem.getTypeDescriptionDescriptionAsString(child))
            print(castypesytem.getTypeDescriptionSuperTypeAsString(child))
            print(castypesytem.getTypeDescriptionFeaturesAsString(child))
            print(' ')
        """

    def test_getTypeDescriptionFeaturesAsString(self):
        castypesytem = TypeSystemParser()
        castypesytem.setTypeAsFile('tests/testing_data/typesystem.xml')
        "print(castypesytem.getTypeDescriptionFeaturesAsString(castypesytem.getTypeDescElements()[1]))"
        self.assertEqual(castypesytem.getElementTag(castypesytem.getTypeDescriptionFeatures(castypesytem.getTypeDescElements()[1])),
                         '{http://uima.apache.org/resourceSpecifier}features')
        self.assertEqual(castypesytem.getElementText(castypesytem.getTypeDescriptionFeatures(castypesytem.getTypeDescElements()[1])),
                         '\n                ')
        self.assertEqual(castypesytem.getElementNamespace(castypesytem.getTypeDescriptionFeatures(castypesytem.getTypeDescElements()[1])),
                         'http://uima.apache.org/resourceSpecifier')
        self.assertEqual(castypesytem.getElementLocalname(castypesytem.getTypeDescriptionFeatures(castypesytem.getTypeDescElements()[1])),
                         'features')

        """
        castypesytem1 = TypeSystemParser()
        atypeDesc= castypesytem.getTypeDescElements()[1]
        features = castypesytem1.getTypeDescriptionFeatures(atypeDesc)
        castypesytem2 = TypeSystemParser()
        """
        "print(castypesytem2.getTypeDescriptionFeaturesAsString(atypeDesc))"

    def test_findTypeDescElementByName(self):
        castypesytem = TypeSystemParser()
        castypesytem.setTypeAsFile('tests/testing_data/typesystem.xml')
        docmetadata = castypesytem.findTypeDescElementByName('de.tudarmstadt.ukp.dkpro.core.api.metadata.type.DocumentMetaData')
        self.assertEqual(castypesytem.getElementText(castypesytem.getTypeDescriptionName(docmetadata)),
              'de.tudarmstadt.ukp.dkpro.core.api.metadata.type.DocumentMetaData')

    def test_findTypeDescFeatureByName(self):
        castypesytem = TypeSystemParser()
        castypesytem.setTypeAsFile('tests/testing_data/typesystem.xml')
        fd = castypesytem.findTypeDescFeatureByName('language','de.tudarmstadt.ukp.dkpro.core.api.metadata.type.DocumentMetaData')

        self.assertEqual(castypesytem.getElementText(castypesytem.getFeatureDescName(fd)),'language')
        with self.assertRaises(AttributeError):
            castypesytem.getElementText(None)
