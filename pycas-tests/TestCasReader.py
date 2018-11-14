'''
Created on Dec 25, 2016

@author: Dibyojyoti
unit test cases to check CasXmi functionality
'''
import unittest2 as unittest

from pycas.type.cas.CAS_Type import CAS_Type
from pycas.type.cas.Feature import Feature
from pycas.cas.core.FeatureStructure import FeatureStructure
from pycas.cas.core.TOP import TOP
from pycas.cas.core.Annotation import Annotation
from pycas.cas.core.SofaFS import SofaFS
from pycas.cas.core.CAS import CAS
from pycas.cas.core.CasFactory import CasFactory
from pycas.cas.writer.XmiWriter import XmiWriter
from pycas.type.cas.TypeSystemFactory import TypeSystemFactory
from pycas.type.cas.TypeDescription import TypeDescription

class TestStringMethods(unittest.TestCase):
    # can't instantiate as abstract classes
    def test_abstract(self):
        self.assertEqual('', '')
        with self.assertRaises(TypeError):
            castype = CAS_Type()

        self.assertEqual('', '')
        with self.assertRaises(TypeError):
            featureStructure = FeatureStructure()

    # create a feature
    def test_feature(self):
        typeSystemFilePath = 'tests/testing_data/typesystem.xml'
        typesystem = TypeSystemFactory.readTypeSystem(self, typeSystemFilePath)
        typeFsArray = typesystem.getType('uima.cas.FSArray')
        typeSa = typesystem.getType('de.tudarmstadt.ukp.dkpro.core.api.anomaly.type.SuggestedAction')
        aFeature = Feature('de.tudarmstadt.ukp.dkpro.core.api.anomaly.type.Anomaly','suggestions')
        aFeature.description = ''
        aFeature.rangeType = typeFsArray
        aFeature.elementType = typeSa

        self.assertEqual(aFeature.domain, 'de.tudarmstadt.ukp.dkpro.core.api.anomaly.type.Anomaly')
        self.assertEqual(aFeature.name, 'suggestions')
        self.assertEqual(aFeature.description, '')
        self.assertEqual(aFeature.rangeType, typeFsArray)
        self.assertEqual(aFeature.elementType.name, typeSa.name)

    # use of setListValue and getListValue
    def test_ListValsetNget(self):

        typeSystemFilePath = 'tests/testing_data/typesystem.xml'
        typesystem = TypeSystemFactory.readTypeSystem(self, typeSystemFilePath)
        fstype4 = typesystem.getType('de.tudarmstadt.ukp.dkpro.core.api.metadata.type.TagDescription')
        fsTagDesc1 = TOP(fstype4,1,typesystem)
        aFeature = Feature(fsTagDesc1.FStype,'name')
        aFeature.description = ''
        aFeature.rangeType = 'uima.cas.String'
        listval=[]
        listval.append('#')
        fsTagDesc1.setListValue(aFeature, aFeature.rangeType, listval)
        self.assertEqual(' '.join(fsTagDesc1.getListValue(aFeature)),'#')

    # checking of setListValue and getListValue exceptions
    def test_setListVal_Fail(self):
        typeSystemFilePath = 'tests/testing_data/typesystem.xml'
        typesystem = TypeSystemFactory.readTypeSystem(self, typeSystemFilePath)
        fstype4 = typesystem.getType('de.tudarmstadt.ukp.dkpro.core.api.metadata.type.TagDescription')
        fsTagDesc1 = TOP(fstype4,1,typesystem)
        aFeature = Feature(fsTagDesc1.FStype,'name')
        aFeature.description = ''
        aFeature.rangeType = 'uima.cas.String'
        listval=[]
        listval.append('#')
        self.assertEqual('','')
        with self.assertRaises(TypeError):
            nonlist= 1
            fsTagDesc1.setListValue(aFeature, aFeature.rangeType, nonlist)
        with self.assertRaises(TypeError):
            nonfeature= 1
            fsTagDesc1.setListValue(nonfeature, aFeature.rangeType, listval)
        with self.assertRaises(TypeError):
            aFeature.rangeType = 'uima.cas.Inetger'
            fsTagDesc1.setListValue(aFeature, aFeature.rangeType, listval)
        with self.assertRaises(TypeError):
            aFeature.rangeType = typesystem.getType('de.tudarmstadt.ukp.dkpro.core.api.lexmorph.type.pos.POS')

            fsTagDesc1.setListValue(aFeature, aFeature.rangeType, listval)
        with self.assertRaises(TypeError):
            aFeature.rangeType = 'uima.cas.Integer'
            aFeature.elementType = 'uima.cas.String'
            fsTagDesc1.setListValue(aFeature, aFeature.elementType, listval)

    # use of setStringValue and getStringValue
    def test_StringValsetNget(self):
        typeSystemFilePath = 'tests/testing_data/typesystem.xml'
        typesystem = TypeSystemFactory.readTypeSystem(self, typeSystemFilePath)
        fstype4 = typesystem.getType('de.tudarmstadt.ukp.dkpro.core.api.metadata.type.TagDescription')
        fsTagDesc1 = TOP(fstype4,1,typesystem)
        aFeature = Feature(fsTagDesc1.FStype,'name')
        aFeature.description = ''
        aFeature.elementType = 'uima.cas.String'

        fsTagDesc1.setStringValue(aFeature, "Hello")
        self.assertEqual(fsTagDesc1.getStringValue(aFeature),'Hello')

    # checking of setStringValue and getStringValue exceptions
    def test_setStringVal_Fail(self):
        typeSystemFilePath = 'tests/testing_data/typesystem.xml'
        typesystem = TypeSystemFactory.readTypeSystem(self, typeSystemFilePath)
        fstype4 = typesystem.getType('de.tudarmstadt.ukp.dkpro.core.api.metadata.type.TagDescription')
        fsTagDesc1 = TOP(fstype4,1,typesystem)
        aFeature = Feature(fsTagDesc1.FStype,'name')
        aFeature.description = ''
        aFeature.elementType = 'uima.cas.String'
        self.assertEqual('','')
        with self.assertRaises(TypeError):
            fsTagDesc1.setStringValue(aFeature, 1)
        with self.assertRaises(TypeError):
            nonfeature=1
            fsTagDesc1.setStringValue(nonfeature, '1')
        with self.assertRaises(TypeError):
            aFeature.elementType = None
            fsTagDesc1.setStringValue(aFeature, '1')
        with self.assertRaises(TypeError):
            aFeature.elementType = 'uima.cas.Integer'
            fsTagDesc1.setStringValue(aFeature, '1')


    # use of setBoolValue and getBoolValue
    def test_BoolValsetNget(self):
        typeSystemFilePath = 'tests/testing_data/typesystem.xml'
        typesystem = TypeSystemFactory.readTypeSystem(self, typeSystemFilePath)
        fstype4 = typesystem.getType('de.tudarmstadt.ukp.dkpro.core.api.metadata.type.TagDescription')
        fsTagDesc1 = TOP(fstype4,1,typesystem)
        aFeature = Feature(fsTagDesc1.FStype,'name')
        aFeature.description = ''
        aFeature.elementType = 'uima.cas.Boolean'
        fsTagDesc1.setBoolValue(aFeature, False)
        self.assertEqual(fsTagDesc1.getBoolValue(aFeature),False)

    # checking of setBoolValue and getBoolValue exceptions
    def test_setBoolVal_Fail(self):
        typeSystemFilePath = 'tests/testing_data/typesystem.xml'
        typesystem = TypeSystemFactory.readTypeSystem(self, typeSystemFilePath)
        fstype4 = typesystem.getType('de.tudarmstadt.ukp.dkpro.core.api.metadata.type.TagDescription')
        fsTagDesc1 = TOP(fstype4,1,typesystem)
        aFeature = Feature(fsTagDesc1.FStype,'name')
        aFeature.description = ''
        aFeature.elementType = 'uima.cas.Boolean'
        self.assertEqual('','')
        with self.assertRaises(TypeError):
            fsTagDesc1.setBoolValue(aFeature, 'False')
        with self.assertRaises(TypeError):
            nonfeature=1
            fsTagDesc1.setBoolValue(nonfeature, False)
        with self.assertRaises(TypeError):
            aFeature.elementType = None
            fsTagDesc1.setBoolValue(aFeature, False)
        with self.assertRaises(TypeError):
            aFeature.elementType = 'uima.cas.Integer'
            fsTagDesc1.setBoolValue(aFeature, False)


    # use of setIntValue and getIntValue
    def test_IntValsetNget(self):
        typeSystemFilePath = 'tests/testing_data/typesystem.xml'
        typesystem = TypeSystemFactory.readTypeSystem(self, typeSystemFilePath)
        fstype4 = typesystem.getType('de.tudarmstadt.ukp.dkpro.core.api.metadata.type.TagDescription')
        fsTagDesc1 = TOP(fstype4,1,typesystem)
        aFeature = Feature(fsTagDesc1.FStype,'name')
        aFeature.description = ''
        aFeature.elementType = 'uima.cas.Integer'

        fsTagDesc1.setIntValue(aFeature, 10)
        self.assertEqual(fsTagDesc1.getIntValue(aFeature),10)

    # checking of setIntValue and getIntValue exceptions
    def test_setIntVal_Fail(self):
        typeSystemFilePath = 'tests/testing_data/typesystem.xml'
        typesystem = TypeSystemFactory.readTypeSystem(self, typeSystemFilePath)
        fstype4 = typesystem.getType('de.tudarmstadt.ukp.dkpro.core.api.metadata.type.TagDescription')
        fsTagDesc1 = TOP(fstype4,1,typesystem)
        aFeature = Feature(fsTagDesc1.FStype,'name')
        aFeature.description = ''
        aFeature.elementType = 'uima.cas.Integer'
        self.assertEqual('','')
        with self.assertRaises(TypeError):
            fsTagDesc1.setIntValue(aFeature, '')
        with self.assertRaises(TypeError):
            nonfeature=1
            fsTagDesc1.setIntValue(nonfeature, 10)
        with self.assertRaises(TypeError):
            aFeature.elementType = None
            fsTagDesc1.setIntValue(aFeature, 10)
        with self.assertRaises(TypeError):
            aFeature.elementType = 'uima.cas.String'
            fsTagDesc1.setIntValue(aFeature, 10)

    # use of setLongValue and getLongValue, in python long is also represented using Integer
    def test_LongValsetNget(self):
        typeSystemFilePath = 'tests/testing_data/typesystem.xml'
        typesystem = TypeSystemFactory.readTypeSystem(self, typeSystemFilePath)
        fstype4 = typesystem.getType('de.tudarmstadt.ukp.dkpro.core.api.metadata.type.TagDescription')
        fsTagDesc1 = TOP(fstype4,1,typesystem)
        aFeature = Feature(fsTagDesc1.FStype,'name')
        aFeature.description = ''
        aFeature.elementType = 'uima.cas.Long'

        fsTagDesc1.setLongValue(aFeature, 100000000)
        self.assertEqual(int(fsTagDesc1.getLongValue(aFeature)),100000000)

    # checking of setLongValue and getLongValue exceptions
    def test_setLongVal_Fail(self):
        typeSystemFilePath = 'tests/testing_data/typesystem.xml'
        typesystem = TypeSystemFactory.readTypeSystem(self, typeSystemFilePath)
        fstype4 = typesystem.getType('de.tudarmstadt.ukp.dkpro.core.api.metadata.type.TagDescription')
        fsTagDesc1 = TOP(fstype4,1,typesystem)
        aFeature = Feature(fsTagDesc1.FStype,'name')
        aFeature.description = ''
        aFeature.elementType = 'uima.cas.Integer'
        self.assertEqual('','')
        with self.assertRaises(TypeError):
            fsTagDesc1.setIntValue(aFeature, '')
        with self.assertRaises(TypeError):
            nonfeature=1
            fsTagDesc1.setLongValue(nonfeature, 10000000)
        with self.assertRaises(TypeError):
            aFeature.elementType = None
            fsTagDesc1.setIntValue(aFeature, 100000000)
        with self.assertRaises(TypeError):
            aFeature.elementType = 'uima.cas.String'
            fsTagDesc1.setIntValue(aFeature, 100000000)

    # use of setFloatValue and getFloatValue
    def test_FloatValsetNget(self):
        typeSystemFilePath = 'tests/testing_data/typesystem.xml'
        typesystem = TypeSystemFactory.readTypeSystem(self, typeSystemFilePath)
        fstype4 = typesystem.getType('de.tudarmstadt.ukp.dkpro.core.api.metadata.type.TagDescription')
        fsTagDesc1 = TOP(fstype4,1,typesystem)
        aFeature = Feature(fsTagDesc1.FStype,'name')
        aFeature.description = ''
        aFeature.elementType = 'uima.cas.Float'

        fsTagDesc1.setFloatValue(aFeature, 10.1)
        self.assertEqual(fsTagDesc1.getFloatValue(aFeature),10.1)

    # checking of setFloatValue and getFloatValue exceptions
    def test_setFloatVal_Fail(self):
        typeSystemFilePath = 'tests/testing_data/typesystem.xml'
        typesystem = TypeSystemFactory.readTypeSystem(self, typeSystemFilePath)
        fstype4 = typesystem.getType('de.tudarmstadt.ukp.dkpro.core.api.metadata.type.TagDescription')
        fsTagDesc1 = TOP(fstype4,1,typesystem)
        aFeature = Feature(fsTagDesc1.FStype,'name')
        aFeature.description = ''
        aFeature.elementType = 'uima.cas.Float'
        self.assertEqual('','')
        with self.assertRaises(TypeError):
            fsTagDesc1.setFloatValue(aFeature, '10.1')
        with self.assertRaises(TypeError):
            nonfeature=1
            fsTagDesc1.setFloatValue(nonfeature, 10.1)
        with self.assertRaises(TypeError):
            aFeature.elementType = None
            fsTagDesc1.setFloatValue(aFeature, 10.1)
        with self.assertRaises(TypeError):
            aFeature.elementType = 'uima.cas.String'
            fsTagDesc1.setFloatValue(aFeature, 10.1)

    # use of setComplexValue and getComplexValue, python has complex data type but java does not, so complex are converted to string in python
    def test_ComplexValsetNget(self):
        typeSystemFilePath = 'tests/testing_data/typesystem.xml'
        typesystem = TypeSystemFactory.readTypeSystem(self, typeSystemFilePath)
        fstype4 = typesystem.getType('de.tudarmstadt.ukp.dkpro.core.api.metadata.type.TagDescription')
        fsTagDesc1 = TOP(fstype4,1,typesystem)
        aFeature = Feature(fsTagDesc1.FStype,'name')
        aFeature.description = ''
        aFeature.elementType = 'uima.cas.String'

        fsTagDesc1.setComplexValue(aFeature, 1j)
        self.assertEqual(complex(fsTagDesc1.getComplexValue(aFeature)),1j)

    # checking of setComplexValue and getComplexValue exceptions
    def test_setComplexVal_Fail(self):
        typeSystemFilePath = 'tests/testing_data/typesystem.xml'
        typesystem = TypeSystemFactory.readTypeSystem(self, typeSystemFilePath)
        fstype4 = typesystem.getType('de.tudarmstadt.ukp.dkpro.core.api.metadata.type.TagDescription')
        fsTagDesc1 = TOP(fstype4,1,typesystem)
        aFeature = Feature(fsTagDesc1.FStype,'name')
        aFeature.description = ''
        aFeature.elementType = 'uima.cas.String'
        self.assertEqual('','')
        with self.assertRaises(TypeError):
            fsTagDesc1.setComplexValue(aFeature, 10.1)
        with self.assertRaises(TypeError):
            nonfeature=1
            fsTagDesc1.setComplexValue(nonfeature, 1j)
        with self.assertRaises(TypeError):
            aFeature.elementType = None
            fsTagDesc1.setComplexValue(aFeature, 1j)
        with self.assertRaises(TypeError):
            aFeature.elementType = 'uima.cas.Integer'
            fsTagDesc1.setComplexValue(aFeature, 1j)

    # use of setFeatureValue and getFeatureValue
    def test_FeatureValsetNget(self):
        typeSystemFilePath = 'tests/testing_data/typesystem.xml'
        typesystem = TypeSystemFactory.readTypeSystem(self, typeSystemFilePath)
        tokenType = 'de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token'
        fsTokenType = typesystem.getType(tokenType)
        posType = 'de.tudarmstadt.ukp.dkpro.core.api.lexmorph.type.pos.POS'
        fsPosType = typesystem.getType(posType)

        fsToken = TOP(fsTokenType,1,typesystem)

        aFeature = Feature(fsToken.FStype,'pos')
        aFeature.description = ''
        aFeature.rangeType = typesystem.getType('de.tudarmstadt.ukp.dkpro.core.api.lexmorph.type.pos.POS')

        fsPOS = Annotation(fsPosType,1,typesystem)
        fsPOS.PosValue = "DT"

        fsToken.setFeatureValue(aFeature, fsPOS)
        self.assertEqual(fsToken.getFeatureValue(aFeature),fsPOS)

    # checking of setFeatureValue and getFeatureValue exceptions
    def test_setFeatureVal_Fail(self):
        typeSystemFilePath = 'tests/testing_data/typesystem.xml'
        typesystem = TypeSystemFactory.readTypeSystem(self, typeSystemFilePath)
        fstype4 = typesystem.getType('de.tudarmstadt.ukp.dkpro.core.api.metadata.type.TagDescription')
        fsTagDesc1 = TOP(fstype4,1,typesystem)
        aFeature = Feature(fsTagDesc1.FStype,'name')
        aFeature.description = ''
        aFeature.elementType = typesystem.getType('de.tudarmstadt.ukp.dkpro.core.api.lexmorph.type.pos.POS')

        self.assertEqual('','')
        with self.assertRaises(TypeError):
            fsTagDesc1.setFeatureValue(aFeature, 10.1)
        with self.assertRaises(TypeError):
            nonfeature=1
            fsTagDesc1.setComplexValue(nonfeature, 878)
        with self.assertRaises(TypeError):
            aFeature.elementType = None
            fsTagDesc1.setComplexValue(aFeature, 878)
        with self.assertRaises(TypeError):
            aFeature.elementType = 'uima.cas.Integer'
            fsTagDesc1.setComplexValue(aFeature, 878)

    def test_Annotation(self):
        typeSystemFilePath = 'tests/testing_data/typesystem.xml'
        typesystem = TypeSystemFactory.readTypeSystem(self, typeSystemFilePath)
        fstype4 = typesystem.getType('de.tudarmstadt.ukp.dkpro.core.api.metadata.type.TagDescription')
        sentenceType = 'de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Sentence'
        fsSentenceType = typesystem.getType(sentenceType)

        sofaType = 'uima.cas.Sofa'
        fsSofaType = typesystem.getType(sofaType)
        sofaFs = SofaFS(fsSofaType,2)
        sofaFs.sofaNum = 1
        sofaFs.sofaID = '_InitialView'
        sofaFs.mimeType = 'text'
        sofaFs.sofaString = 'These steps install the basis system requirements'

        fsSentence1 = Annotation(fsSentenceType,102,typesystem)
        fsSentence1.begin = 0
        fsSentence1.end = 115
        #set sofa object directly to the sofa feature
        fsSentence1.sofa = sofaFs

        self.assertEqual(fsSentence1.begin,0)
        self.assertEqual(fsSentence1.end,115)
        self.assertEqual(fsSentence1.sofa,sofaFs)

        fsSentence2 = Annotation(fsSentenceType,107,typesystem)
        fsSentence2.begin = 116
        fsSentence2.end = 152
        fsSentence2.sofa = sofaFs

        self.assertEqual(fsSentence2.begin,116)
        self.assertEqual(fsSentence2.end,152)
        self.assertEqual(fsSentence2.sofa,sofaFs)

    #test retrieving feature
    def test_getFeature(self):
        typeSystemFilePath = 'tests/testing_data/typesystem.xml'
        typesystem = TypeSystemFactory.readTypeSystem(self, typeSystemFilePath)
        posType = 'de.tudarmstadt.ukp.dkpro.core.api.lexmorph.type.pos.POS'
        fsPosType = typesystem.getType(posType)
        artType = 'de.tudarmstadt.ukp.dkpro.core.api.lexmorph.type.pos.ART'
        fsArtType = typesystem.getType(artType)
        tokenType = 'de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token'
        fsTokenType = typesystem.getType(tokenType)

        sofaType = 'uima.cas.Sofa'
        fsSofaType = typesystem.getType(sofaType)
        sofaFs = SofaFS(fsSofaType,2)
        sofaFs.sofaNum = 1
        sofaFs.sofaID = '_InitialView'
        sofaFs.mimeType = 'text'
        sofaFs.sofaString = 'These steps install the basis system requirements'

        fsPOS = Annotation(fsPosType,1,typesystem)
        fsPOS.PosValue = "DT"
        self.assertEqual(fsPOS.PosValue,"DT")

        fsArt1 = Annotation(fsArtType,540,typesystem)
        fsArt1.begin = 0
        fsArt1.end = 5
        fsArt1.sofa = sofaFs
        #the provided setter wrapper of FeatureStructure_Impl enables converting an attribute to be set like this to create a Feature internally for the attribute
        fsArt1.PosValue = "DT"
        self.assertEqual(fsArt1.PosValue,"DT")

        fsToken1 = Annotation(fsTokenType,112,typesystem)
        fsToken1.begin = 0
        fsToken1.end = 5
        fsToken1.sofa = sofaFs
        fsToken1.pos = fsArt1
        self.assertEqual(fsToken1.pos,[fsArt1])

    # test creating cas object
    def test_Cas(self):
        typeSystemFilePath = 'tests/testing_data/typesystem.xml'
        typesystem = TypeSystemFactory.readTypeSystem(self, typeSystemFilePath)
        cas = CAS(typesystem)
        cas.documentText = 'These steps install the basis system requirements'
        cas.sofaMimeType = 'text'

        sentenceType = 'de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Sentence'
        tokenType = 'de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token'
        posType = 'de.tudarmstadt.ukp.dkpro.core.api.lexmorph.type.pos.POS'
        tagDescType = 'de.tudarmstadt.ukp.dkpro.core.api.metadata.type.TagDescription'
        tagSetDescType = 'de.tudarmstadt.ukp.dkpro.core.api.metadata.type.TagsetDescription'

        fsSentence1 = cas.createFS(sentenceType);
        cas.addToIndex(fsSentence1)
        #check empty FS
        self.assertEqual(fsSentence1.getFeatureValsAsDictList(),[])

        #throws error, 1, 'as FSid is already occupied' , assigned to auto generated Sofa FS
        self.assertEqual('','')
        with self.assertRaises(ValueError):
            fsSentence2 = cas.createFS(sentenceType, { 'begin': 10, 'end': 20},1);

        fsPOS = cas.createFS(posType,{ 'PosValue': 'NN'},3);
        cas.addToIndex(fsPOS)
        fsPOS.PosValue = 'Noun'
        #throws error, need to provide feature as dictionary as second argument
        self.assertEqual('','')
        with self.assertRaises(TypeError):
            fsPOSx = cas.createAnnotation(posType,2);
        #throws error, as 3 is already set as FS id , lower than 3 can not be set by user
        self.assertEqual('','')
        with self.assertRaises(ValueError):
            fsPOSx = cas.createAnnotation(posType,{ 'PosValue': 'NN'},2);
        #throws error, needs both begin and end
        self.assertEqual('','')
        with self.assertRaises(ValueError):
            fsPOSx = cas.createAnnotation(posType,{ 'begin': 10,'PosValue': 'NN'},4);

        #create a valid annotation FS
        fsPOS = cas.createAnnotation(posType,{ 'begin': 0,'end': 5,'PosValue': 'NN'});
        #add it to index
        cas.addToIndex(fsPOS)
        fsPOS1 = cas.createAnnotation(posType,{ 'begin': 0,'end': 5});
        fsPOS1.PosValue = 'NN'
        cas.addToIndex(fsPOS1)
        fsToken1 = cas.createAnnotation(tokenType,{ 'begin': 0, 'end': 5, 'pos': fsPOS});
        cas.addToIndex(fsToken1)

        tdlist = []
        fstagDesc1 = cas.createFS(tagDescType, {'name' :'#'})
        tdlist.append(fstagDesc1)
        fstagDesc2 = cas.createFS(tagDescType, {'name' :'$'})
        tdlist.append(fstagDesc2)
        fstagDesc3 = cas.createFS(tagDescType, {'name' :'-LRB-'})
        tdlist.append(fstagDesc3)

        fstagSetDesc = cas.createAnnotation(tagSetDescType,{'begin': 0, 'end': 152,
                        'layer': 'de.tudarmstadt.ukp.dkpro.core.api.lexmorph.type.pos.POS','name': 'ptb','tags':tdlist})
        cas.addToIndex(fstagSetDesc)
        #get all FS in index
        for e in cas.getAnnotationIndex():
            #check FSid
            if (e.FStype.name == "uima.cas.Sofa"):
                self.assertEqual(e.FSid,1)

            if (e.FStype.name == "de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Sentence"):
                self.assertEqual(e.FSid,2)
            if (e.FStype.name == "de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token"):
                self.assertEqual(e.FSid,7)
            #check FS type
            if (e.FSid == 1):
                self.assertEqual(e.FStype.name,"uima.cas.Sofa")
            if (e.FSid == 2):
                self.assertEqual(e.FStype.name,"de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Sentence")
            if (e.FSid == 7):
                self.assertEqual(e.FStype.name,"de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token")
        #check sofa
        self.assertEqual(cas.sofaMimeType,cas.sofaFS.mimeType)
        self.assertEqual(1,cas.sofaFS.sofaNum)
        self.assertEqual('_InitialView',cas.sofaFS.sofaID)
        self.assertEqual(cas.documentText,cas.sofaFS.sofaString)

        tokens = cas.getAnnotation('de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token')
        self.assertEqual(tokens[0].getCoveredText(),"These")

    #example of parsing the whole CasXmi file to a full object structure and writing back from the object structure
    def test_casbuild(self):
        caf = CasFactory()
        cas = caf.buildCAS('tests/testing_data/document3.txt.xmi', 'tests/testing_data/typesystem.xml')

        """
        for e in cas.getAnnotationIndex():
            print(e.FSid,e.FStype)
            print(e.getFeatureValsAsDictList())
        """

        xmiwriter = XmiWriter()
        #provide correct path
        xmiwriter.write(cas, 'tests/testing_data/document5.txt.xmi')

    #example of creating type system object
    def test_typeysfact(self):
        typesystem = TypeSystemFactory.readTypeSystem(self, 'tests/testing_data/typesystem.xml')

        """
        for tdesc in typesystem.getAllTypeDesc():
            for fdesc in tdesc.getAllFeature():
                print(tdesc.name,fdesc.name)
        """
if __name__ == '__main__':
    unittest.main()
