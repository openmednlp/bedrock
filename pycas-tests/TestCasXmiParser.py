'''
Created on Dec 12, 2016
unit test cases to check CasXmiParser functionality
@author: Dibyojyoti
'''
import unittest2 as unittest
from pycas.cas.parse.CasXmiParser import CasXmiParser
import lxml

class TestCasXmiParserMethods(unittest.TestCase):
    def test_witeXmiAsFile(self):
        casxmi = CasXmiParser()
        casxmi.setXmiAsFile('tests/testing_data/document1.txt.xmi')
        #provide proper path before running
        """casxmi.witeXmiAsFile('C:/Users/Dibyojyoti/Desktop/scriptop/document1_op.txt.xmi')
        casxmi1 = CasXmiParser()
        casxmi1.setXmiAsFile('C:/Users/Dibyojyoti/Desktop/scriptop/document1_op.txt.xmi')
        self.assertEqual(casxmi.getXmiAsString(),casxmi1.getXmiAsString())
        """
    def test_root(self):
        casxmi = CasXmiParser()
        casxmi.setXmiAsFile('tests/testing_data/document1.txt.xmi')
        casxmi1 = CasXmiParser()
        self.assertEqual(casxmi1.getTag(casxmi.getRootElement()),'{http://www.omg.org/XMI}XMI')
        self.assertEqual(casxmi1.getLocalname(casxmi.getRootElement()),'XMI')
        self.assertEqual(casxmi1.getNamespace(casxmi.getRootElement()),'http://www.omg.org/XMI')
        self.assertEqual(casxmi.getRootTagAsDict(), {'XMI': 'http://www.omg.org/XMI'})
        self.assertEqual(casxmi.getRootAttribteNames(), ['{http://www.omg.org/XMI}version'])
        self.assertEqual(casxmi.getRootAttributesAsDict(),{'{http://www.omg.org/XMI}version': '2.0'})
        self.assertEqual(casxmi.getRootAttributesAsList(),[('{http://www.omg.org/XMI}version', '2.0')])

    def test_casnull(self):
        casxmi = CasXmiParser()
        casxmi.setXmiAsFile('tests/testing_data/document1.txt.xmi')
        str1='''<cas:NULL xmlns:cas="http:///uima/cas.ecore" xmlns:xmi="http://www.omg.org/XMI" xmlns:pos="http:///de/tudarmstadt/ukp/dkpro/core/api/lexmorph/type/pos.ecore" xmlns:tcas="http:///uima/tcas.ecore" xmlns:tweet="http:///de/tudarmstadt/ukp/dkpro/core/api/lexmorph/type/pos/tweet.ecore" xmlns:morph="http:///de/tudarmstadt/ukp/dkpro/core/api/lexmorph/type/morph.ecore" xmlns:type3="http:///de/tudarmstadt/ukp/dkpro/core/api/frequency/tfidf/type.ecore" xmlns:dependency="http:///de/tudarmstadt/ukp/dkpro/core/api/syntax/type/dependency.ecore" xmlns:type7="http:///de/tudarmstadt/ukp/dkpro/core/api/semantics/type.ecore" xmlns:type9="http:///de/tudarmstadt/ukp/dkpro/core/api/transform/type.ecore" xmlns:type="http:///de/tudarmstadt/ukp/dkpro/core/api/anomaly/type.ecore" xmlns:type8="http:///de/tudarmstadt/ukp/dkpro/core/api/syntax/type.ecore" xmlns:type4="http:///de/tudarmstadt/ukp/dkpro/core/api/metadata/type.ecore" xmlns:type5="http:///de/tudarmstadt/ukp/dkpro/core/api/ner/type.ecore" xmlns:type6="http:///de/tudarmstadt/ukp/dkpro/core/api/segmentation/type.ecore" xmlns:type2="http:///de/tudarmstadt/ukp/dkpro/core/api/coref/type.ecore" xmlns:constituent="http:///de/tudarmstadt/ukp/dkpro/core/api/syntax/type/constituent.ecore" xmlns:chunk="http:///de/tudarmstadt/ukp/dkpro/core/api/syntax/type/chunk.ecore" xmi:id="0"/>\n\n'''
        self.assertEqual(casxmi.convertChildToString(casxmi.getCasNullChild()),str1)

    def test_cassofa(self):
        casxmi = CasXmiParser()
        casxmi.setXmiAsFile('tests/testing_data/document1.txt.xmi')
        str1='''<cas:Sofa xmlns:cas="http:///uima/cas.ecore" xmlns:xmi="http://www.omg.org/XMI" xmlns:pos="http:///de/tudarmstadt/ukp/dkpro/core/api/lexmorph/type/pos.ecore" xmlns:tcas="http:///uima/tcas.ecore" xmlns:tweet="http:///de/tudarmstadt/ukp/dkpro/core/api/lexmorph/type/pos/tweet.ecore" xmlns:morph="http:///de/tudarmstadt/ukp/dkpro/core/api/lexmorph/type/morph.ecore" xmlns:type3="http:///de/tudarmstadt/ukp/dkpro/core/api/frequency/tfidf/type.ecore" xmlns:dependency="http:///de/tudarmstadt/ukp/dkpro/core/api/syntax/type/dependency.ecore" xmlns:type7="http:///de/tudarmstadt/ukp/dkpro/core/api/semantics/type.ecore" xmlns:type9="http:///de/tudarmstadt/ukp/dkpro/core/api/transform/type.ecore" xmlns:type="http:///de/tudarmstadt/ukp/dkpro/core/api/anomaly/type.ecore" xmlns:type8="http:///de/tudarmstadt/ukp/dkpro/core/api/syntax/type.ecore" xmlns:type4="http:///de/tudarmstadt/ukp/dkpro/core/api/metadata/type.ecore" xmlns:type5="http:///de/tudarmstadt/ukp/dkpro/core/api/ner/type.ecore" xmlns:type6="http:///de/tudarmstadt/ukp/dkpro/core/api/segmentation/type.ecore" xmlns:type2="http:///de/tudarmstadt/ukp/dkpro/core/api/coref/type.ecore" xmlns:constituent="http:///de/tudarmstadt/ukp/dkpro/core/api/syntax/type/constituent.ecore" xmlns:chunk="http:///de/tudarmstadt/ukp/dkpro/core/api/syntax/type/chunk.ecore" xmi:id="878" sofaNum="1" sofaID="_InitialView" mimeType="text" sofaString="These steps install the basis system requirements needed to implement DKPro Core pipelines using the Java language. They need to be performed only once."/>\n\n'''
        self.assertEqual(casxmi.convertChildToString(casxmi.getCasSofaChild()),str1)

    def test_casview(self):
        casxmi = CasXmiParser()
        casxmi.setXmiAsFile('tests/testing_data/document1.txt.xmi')
        str1='''<cas:View xmlns:cas="http:///uima/cas.ecore" xmlns:pos="http:///de/tudarmstadt/ukp/dkpro/core/api/lexmorph/type/pos.ecore" xmlns:tcas="http:///uima/tcas.ecore" xmlns:xmi="http://www.omg.org/XMI" xmlns:tweet="http:///de/tudarmstadt/ukp/dkpro/core/api/lexmorph/type/pos/tweet.ecore" xmlns:morph="http:///de/tudarmstadt/ukp/dkpro/core/api/lexmorph/type/morph.ecore" xmlns:type3="http:///de/tudarmstadt/ukp/dkpro/core/api/frequency/tfidf/type.ecore" xmlns:dependency="http:///de/tudarmstadt/ukp/dkpro/core/api/syntax/type/dependency.ecore" xmlns:type7="http:///de/tudarmstadt/ukp/dkpro/core/api/semantics/type.ecore" xmlns:type9="http:///de/tudarmstadt/ukp/dkpro/core/api/transform/type.ecore" xmlns:type="http:///de/tudarmstadt/ukp/dkpro/core/api/anomaly/type.ecore" xmlns:type8="http:///de/tudarmstadt/ukp/dkpro/core/api/syntax/type.ecore" xmlns:type4="http:///de/tudarmstadt/ukp/dkpro/core/api/metadata/type.ecore" xmlns:type5="http:///de/tudarmstadt/ukp/dkpro/core/api/ner/type.ecore" xmlns:type6="http:///de/tudarmstadt/ukp/dkpro/core/api/segmentation/type.ecore" xmlns:type2="http:///de/tudarmstadt/ukp/dkpro/core/api/coref/type.ecore" xmlns:constituent="http:///de/tudarmstadt/ukp/dkpro/core/api/syntax/type/constituent.ecore" xmlns:chunk="http:///de/tudarmstadt/ukp/dkpro/core/api/syntax/type/chunk.ecore" sofa="878" members="91 102 107 112 122 132 142 152 162 172 182 192 202 212 222 232 242 252 262 272 282 292 302 312 322 332 342 352 362 372 485 426 540 545 550 555 560 565 570 575 580 585 590 595 600 605 610 615 620 625 630 635 640 645 650 655 660 665 670 678 686 694 702 710 718 726 734 742 750 758 766 774 782 790 798 806 814 822 830 838 846 854 862 870"/>\n\n'''
        self.assertEqual(casxmi.convertChildToString(casxmi.getCasViewChild()),str1)
        "print(casxmi.getCasChildren())"
        "print(casxmi.getNonCasChildren())"

    def test_findChildByLocalname(self):
        casxmi = CasXmiParser()
        casxmi.setXmiAsFile('tests/testing_data/document1.txt.xmi')
        str1 = '''<type6:Sentence xmlns:type6="http:///de/tudarmstadt/ukp/dkpro/core/api/segmentation/type.ecore" xmlns:xmi="http://www.omg.org/XMI" xmlns:pos="http:///de/tudarmstadt/ukp/dkpro/core/api/lexmorph/type/pos.ecore" xmlns:tcas="http:///uima/tcas.ecore" xmlns:cas="http:///uima/cas.ecore" xmlns:tweet="http:///de/tudarmstadt/ukp/dkpro/core/api/lexmorph/type/pos/tweet.ecore" xmlns:morph="http:///de/tudarmstadt/ukp/dkpro/core/api/lexmorph/type/morph.ecore" xmlns:type3="http:///de/tudarmstadt/ukp/dkpro/core/api/frequency/tfidf/type.ecore" xmlns:dependency="http:///de/tudarmstadt/ukp/dkpro/core/api/syntax/type/dependency.ecore" xmlns:type7="http:///de/tudarmstadt/ukp/dkpro/core/api/semantics/type.ecore" xmlns:type9="http:///de/tudarmstadt/ukp/dkpro/core/api/transform/type.ecore" xmlns:type="http:///de/tudarmstadt/ukp/dkpro/core/api/anomaly/type.ecore" xmlns:type8="http:///de/tudarmstadt/ukp/dkpro/core/api/syntax/type.ecore" xmlns:type4="http:///de/tudarmstadt/ukp/dkpro/core/api/metadata/type.ecore" xmlns:type5="http:///de/tudarmstadt/ukp/dkpro/core/api/ner/type.ecore" xmlns:type2="http:///de/tudarmstadt/ukp/dkpro/core/api/coref/type.ecore" xmlns:constituent="http:///de/tudarmstadt/ukp/dkpro/core/api/syntax/type/constituent.ecore" xmlns:chunk="http:///de/tudarmstadt/ukp/dkpro/core/api/syntax/type/chunk.ecore" xmi:id="102" sofa="878" begin="0" end="115"/>\n\n'''
        self.assertEqual(casxmi.convertChildToString(casxmi.findChildByLocalname('Sentence')),str1)

    def test_findChildByTag(self):
        casxmi = CasXmiParser()
        casxmi.setXmiAsFile('tests/testing_data/document1.txt.xmi')
        str1='''<type6:Sentence xmlns:type6="http:///de/tudarmstadt/ukp/dkpro/core/api/segmentation/type.ecore" xmlns:xmi="http://www.omg.org/XMI" xmlns:pos="http:///de/tudarmstadt/ukp/dkpro/core/api/lexmorph/type/pos.ecore" xmlns:tcas="http:///uima/tcas.ecore" xmlns:cas="http:///uima/cas.ecore" xmlns:tweet="http:///de/tudarmstadt/ukp/dkpro/core/api/lexmorph/type/pos/tweet.ecore" xmlns:morph="http:///de/tudarmstadt/ukp/dkpro/core/api/lexmorph/type/morph.ecore" xmlns:type3="http:///de/tudarmstadt/ukp/dkpro/core/api/frequency/tfidf/type.ecore" xmlns:dependency="http:///de/tudarmstadt/ukp/dkpro/core/api/syntax/type/dependency.ecore" xmlns:type7="http:///de/tudarmstadt/ukp/dkpro/core/api/semantics/type.ecore" xmlns:type9="http:///de/tudarmstadt/ukp/dkpro/core/api/transform/type.ecore" xmlns:type="http:///de/tudarmstadt/ukp/dkpro/core/api/anomaly/type.ecore" xmlns:type8="http:///de/tudarmstadt/ukp/dkpro/core/api/syntax/type.ecore" xmlns:type4="http:///de/tudarmstadt/ukp/dkpro/core/api/metadata/type.ecore" xmlns:type5="http:///de/tudarmstadt/ukp/dkpro/core/api/ner/type.ecore" xmlns:type2="http:///de/tudarmstadt/ukp/dkpro/core/api/coref/type.ecore" xmlns:constituent="http:///de/tudarmstadt/ukp/dkpro/core/api/syntax/type/constituent.ecore" xmlns:chunk="http:///de/tudarmstadt/ukp/dkpro/core/api/syntax/type/chunk.ecore" xmi:id="102" sofa="878" begin="0" end="115"/>\n\n'''
        self.assertEqual(casxmi.convertChildToString(
            casxmi.findChildByTag('{http:///de/tudarmstadt/ukp/dkpro/core/api/segmentation/type.ecore}Sentence')),str1)

    def test_findChildByNamespace(self):
        casxmi = CasXmiParser()
        casxmi.setXmiAsFile('tests/testing_data/document1.txt.xmi')
        str1='''<type6:Sentence xmlns:type6="http:///de/tudarmstadt/ukp/dkpro/core/api/segmentation/type.ecore" xmlns:xmi="http://www.omg.org/XMI" xmlns:pos="http:///de/tudarmstadt/ukp/dkpro/core/api/lexmorph/type/pos.ecore" xmlns:tcas="http:///uima/tcas.ecore" xmlns:cas="http:///uima/cas.ecore" xmlns:tweet="http:///de/tudarmstadt/ukp/dkpro/core/api/lexmorph/type/pos/tweet.ecore" xmlns:morph="http:///de/tudarmstadt/ukp/dkpro/core/api/lexmorph/type/morph.ecore" xmlns:type3="http:///de/tudarmstadt/ukp/dkpro/core/api/frequency/tfidf/type.ecore" xmlns:dependency="http:///de/tudarmstadt/ukp/dkpro/core/api/syntax/type/dependency.ecore" xmlns:type7="http:///de/tudarmstadt/ukp/dkpro/core/api/semantics/type.ecore" xmlns:type9="http:///de/tudarmstadt/ukp/dkpro/core/api/transform/type.ecore" xmlns:type="http:///de/tudarmstadt/ukp/dkpro/core/api/anomaly/type.ecore" xmlns:type8="http:///de/tudarmstadt/ukp/dkpro/core/api/syntax/type.ecore" xmlns:type4="http:///de/tudarmstadt/ukp/dkpro/core/api/metadata/type.ecore" xmlns:type5="http:///de/tudarmstadt/ukp/dkpro/core/api/ner/type.ecore" xmlns:type2="http:///de/tudarmstadt/ukp/dkpro/core/api/coref/type.ecore" xmlns:constituent="http:///de/tudarmstadt/ukp/dkpro/core/api/syntax/type/constituent.ecore" xmlns:chunk="http:///de/tudarmstadt/ukp/dkpro/core/api/syntax/type/chunk.ecore" xmi:id="102" sofa="878" begin="0" end="115"/>\n\n'''
        self.assertEqual(casxmi.convertChildToString(
            casxmi.findChildByNamespace('http:///de/tudarmstadt/ukp/dkpro/core/api/segmentation/type.ecore')),str1)

    def test_findChildrenByLocalname(self):
        casxmi = CasXmiParser()
        casxmi.setXmiAsFile('tests/testing_data/document1.txt.xmi')
        str1='''<type6:Sentence xmlns:type6="http:///de/tudarmstadt/ukp/dkpro/core/api/segmentation/type.ecore" xmlns:xmi="http://www.omg.org/XMI" xmlns:pos="http:///de/tudarmstadt/ukp/dkpro/core/api/lexmorph/type/pos.ecore" xmlns:tcas="http:///uima/tcas.ecore" xmlns:cas="http:///uima/cas.ecore" xmlns:tweet="http:///de/tudarmstadt/ukp/dkpro/core/api/lexmorph/type/pos/tweet.ecore" xmlns:morph="http:///de/tudarmstadt/ukp/dkpro/core/api/lexmorph/type/morph.ecore" xmlns:type3="http:///de/tudarmstadt/ukp/dkpro/core/api/frequency/tfidf/type.ecore" xmlns:dependency="http:///de/tudarmstadt/ukp/dkpro/core/api/syntax/type/dependency.ecore" xmlns:type7="http:///de/tudarmstadt/ukp/dkpro/core/api/semantics/type.ecore" xmlns:type9="http:///de/tudarmstadt/ukp/dkpro/core/api/transform/type.ecore" xmlns:type="http:///de/tudarmstadt/ukp/dkpro/core/api/anomaly/type.ecore" xmlns:type8="http:///de/tudarmstadt/ukp/dkpro/core/api/syntax/type.ecore" xmlns:type4="http:///de/tudarmstadt/ukp/dkpro/core/api/metadata/type.ecore" xmlns:type5="http:///de/tudarmstadt/ukp/dkpro/core/api/ner/type.ecore" xmlns:type2="http:///de/tudarmstadt/ukp/dkpro/core/api/coref/type.ecore" xmlns:constituent="http:///de/tudarmstadt/ukp/dkpro/core/api/syntax/type/constituent.ecore" xmlns:chunk="http:///de/tudarmstadt/ukp/dkpro/core/api/syntax/type/chunk.ecore" xmi:id="102" sofa="878" begin="0" end="115"/>\n\n'''
        self.assertEqual(casxmi.convertChildToString(casxmi.findChildrenByLocalname('Sentence')[0]),str1)

    def test_findChildrenByTag(self):
        casxmi = CasXmiParser()
        casxmi.setXmiAsFile('tests/testing_data/document1.txt.xmi')
        str1='''<type6:Sentence xmlns:type6="http:///de/tudarmstadt/ukp/dkpro/core/api/segmentation/type.ecore" xmlns:xmi="http://www.omg.org/XMI" xmlns:pos="http:///de/tudarmstadt/ukp/dkpro/core/api/lexmorph/type/pos.ecore" xmlns:tcas="http:///uima/tcas.ecore" xmlns:cas="http:///uima/cas.ecore" xmlns:tweet="http:///de/tudarmstadt/ukp/dkpro/core/api/lexmorph/type/pos/tweet.ecore" xmlns:morph="http:///de/tudarmstadt/ukp/dkpro/core/api/lexmorph/type/morph.ecore" xmlns:type3="http:///de/tudarmstadt/ukp/dkpro/core/api/frequency/tfidf/type.ecore" xmlns:dependency="http:///de/tudarmstadt/ukp/dkpro/core/api/syntax/type/dependency.ecore" xmlns:type7="http:///de/tudarmstadt/ukp/dkpro/core/api/semantics/type.ecore" xmlns:type9="http:///de/tudarmstadt/ukp/dkpro/core/api/transform/type.ecore" xmlns:type="http:///de/tudarmstadt/ukp/dkpro/core/api/anomaly/type.ecore" xmlns:type8="http:///de/tudarmstadt/ukp/dkpro/core/api/syntax/type.ecore" xmlns:type4="http:///de/tudarmstadt/ukp/dkpro/core/api/metadata/type.ecore" xmlns:type5="http:///de/tudarmstadt/ukp/dkpro/core/api/ner/type.ecore" xmlns:type2="http:///de/tudarmstadt/ukp/dkpro/core/api/coref/type.ecore" xmlns:constituent="http:///de/tudarmstadt/ukp/dkpro/core/api/syntax/type/constituent.ecore" xmlns:chunk="http:///de/tudarmstadt/ukp/dkpro/core/api/syntax/type/chunk.ecore" xmi:id="102" sofa="878" begin="0" end="115"/>\n\n'''
        self.assertEqual(casxmi.convertChildToString(
            casxmi.findChildrenByTag('{http:///de/tudarmstadt/ukp/dkpro/core/api/segmentation/type.ecore}Sentence')[0]),str1)

    def test_findChildrenByNamespace(self):
        casxmi = CasXmiParser()
        casxmi.setXmiAsFile('tests/testing_data/document1.txt.xmi')
        str1='''<type6:Sentence xmlns:type6="http:///de/tudarmstadt/ukp/dkpro/core/api/segmentation/type.ecore" xmlns:xmi="http://www.omg.org/XMI" xmlns:pos="http:///de/tudarmstadt/ukp/dkpro/core/api/lexmorph/type/pos.ecore" xmlns:tcas="http:///uima/tcas.ecore" xmlns:cas="http:///uima/cas.ecore" xmlns:tweet="http:///de/tudarmstadt/ukp/dkpro/core/api/lexmorph/type/pos/tweet.ecore" xmlns:morph="http:///de/tudarmstadt/ukp/dkpro/core/api/lexmorph/type/morph.ecore" xmlns:type3="http:///de/tudarmstadt/ukp/dkpro/core/api/frequency/tfidf/type.ecore" xmlns:dependency="http:///de/tudarmstadt/ukp/dkpro/core/api/syntax/type/dependency.ecore" xmlns:type7="http:///de/tudarmstadt/ukp/dkpro/core/api/semantics/type.ecore" xmlns:type9="http:///de/tudarmstadt/ukp/dkpro/core/api/transform/type.ecore" xmlns:type="http:///de/tudarmstadt/ukp/dkpro/core/api/anomaly/type.ecore" xmlns:type8="http:///de/tudarmstadt/ukp/dkpro/core/api/syntax/type.ecore" xmlns:type4="http:///de/tudarmstadt/ukp/dkpro/core/api/metadata/type.ecore" xmlns:type5="http:///de/tudarmstadt/ukp/dkpro/core/api/ner/type.ecore" xmlns:type2="http:///de/tudarmstadt/ukp/dkpro/core/api/coref/type.ecore" xmlns:constituent="http:///de/tudarmstadt/ukp/dkpro/core/api/syntax/type/constituent.ecore" xmlns:chunk="http:///de/tudarmstadt/ukp/dkpro/core/api/syntax/type/chunk.ecore" xmi:id="102" sofa="878" begin="0" end="115"/>\n\n'''
        self.assertEqual(casxmi.convertChildToString(
            casxmi.findChildrenByNamespace('http:///de/tudarmstadt/ukp/dkpro/core/api/segmentation/type.ecore')[0]),str1)

    def test_getChildAttributesAsDict(self):
        casxmi = CasXmiParser()
        casxmi.setXmiAsFile('tests/testing_data/document1.txt.xmi')
        self.assertEqual(casxmi.getChildAttributesAsDict(casxmi.findChildByLocalname('Sentence')),
              {'end': '115', 'sofa': '878', '{http://www.omg.org/XMI}id': '102', 'begin': '0'})

    def test_findChildByAttribute(self):
        casxmi = CasXmiParser()
        casxmi.setXmiAsFile('tests/testing_data/document1.txt.xmi')
        str1='''<type4:DocumentMetaData xmlns:type4="http:///de/tudarmstadt/ukp/dkpro/core/api/metadata/type.ecore" xmlns:xmi="http://www.omg.org/XMI" xmlns:pos="http:///de/tudarmstadt/ukp/dkpro/core/api/lexmorph/type/pos.ecore" xmlns:tcas="http:///uima/tcas.ecore" xmlns:cas="http:///uima/cas.ecore" xmlns:tweet="http:///de/tudarmstadt/ukp/dkpro/core/api/lexmorph/type/pos/tweet.ecore" xmlns:morph="http:///de/tudarmstadt/ukp/dkpro/core/api/lexmorph/type/morph.ecore" xmlns:type3="http:///de/tudarmstadt/ukp/dkpro/core/api/frequency/tfidf/type.ecore" xmlns:dependency="http:///de/tudarmstadt/ukp/dkpro/core/api/syntax/type/dependency.ecore" xmlns:type7="http:///de/tudarmstadt/ukp/dkpro/core/api/semantics/type.ecore" xmlns:type9="http:///de/tudarmstadt/ukp/dkpro/core/api/transform/type.ecore" xmlns:type="http:///de/tudarmstadt/ukp/dkpro/core/api/anomaly/type.ecore" xmlns:type8="http:///de/tudarmstadt/ukp/dkpro/core/api/syntax/type.ecore" xmlns:type5="http:///de/tudarmstadt/ukp/dkpro/core/api/ner/type.ecore" xmlns:type6="http:///de/tudarmstadt/ukp/dkpro/core/api/segmentation/type.ecore" xmlns:type2="http:///de/tudarmstadt/ukp/dkpro/core/api/coref/type.ecore" xmlns:constituent="http:///de/tudarmstadt/ukp/dkpro/core/api/syntax/type/constituent.ecore" xmlns:chunk="http:///de/tudarmstadt/ukp/dkpro/core/api/syntax/type/chunk.ecore" xmi:id="91" sofa="878" begin="0" end="152" language="en" documentTitle="document1.txt" documentId="document1.txt" documentUri="file:/C:/Users/Dibyojyoti/Desktop/scriptip/document1.txt" collectionId="file:/C:/Users/Dibyojyoti/Desktop/scriptip/" documentBaseUri="file:/C:/Users/Dibyojyoti/Desktop/scriptip/" isLastSegment="false"/>\n'''
        self.assertEqual(lxml.etree.tostring(casxmi.findChildByAttribute('sofa')).decode("utf-8"),str1)

    def test_getChildTagAsDict(self):
        casxmi = CasXmiParser()
        casxmi.setXmiAsFile('tests/testing_data/document1.txt.xmi')
        self.assertEqual(casxmi.getRootElement().items()[0],('{http://www.omg.org/XMI}version', '2.0'))
        self.assertEqual(casxmi.getChildTagAsDict(casxmi.getCasSofaChild()),{'Sofa': 'http:///uima/cas.ecore'})

    def test_getChildAttribteNames(self):
        casxmi = CasXmiParser()
        casxmi.setXmiAsFile('tests/testing_data/document1.txt.xmi')
        for child in casxmi.getRootElement():
            self.assertEqual(casxmi.getTag(child),'{http:///uima/cas.ecore}NULL')
            self.assertEqual(casxmi.getChildIndex(child), 0)
            for name, value in casxmi.getChildAttributesAsList(child):
                self.assertEqual(name,'{http://www.omg.org/XMI}id');
                self.assertEqual(value,'0');
            break

    def test_others(self):
        casxmi = CasXmiParser()
        casxmi.setXmiAsFile('tests/testing_data/document1.txt.xmi')
        """
        print('all attributes in root');
        print(casxmi.getRootKeys);
        for name, value in casxmi.getRootAttributesAsList():
            if(casxmi.getNamespace(name) !=None):
                print(casxmi.getNamespace(name),':',casxmi.getLocalname(name),' = ',value)
            else:
                print(name,'=',value);
        """
        """
        elementType="{http:///de/tudarmstadt/ukp/dkpro/core/api/metadata/type.ecore}TagDescription"
        """
        """
        elementType="{http:///de/tudarmstadt/ukp/dkpro/core/api/metadata/type.ecore}TagsetDescription"
        """
        """
        elementType="{http:///de/tudarmstadt/ukp/dkpro/core/api/metadata/type.ecore}DocumentMetaData"
        """
        """
        elementType="cas"
        """

        """
        print('filter tags ');
        for child in casxmi.getChildElementsFilterBytag(elementType):
            print('******child element =',casxmi.getChildTag(child),'   at index : ',casxmi.getChildIndex(child),'   ******')
            print('tagname: ',casxmi.getLocalname(child.tag),' namespace: ',casxmi.getNamespace(child.tag))
            print(sorted(child.keys()));
            for name, value in casxmi.getChildAttributesAsList(child):
                if(casxmi.getNamespace(name) !=None):
                    print(casxmi.getNamespace(name),':',casxmi.getLocalname(name),' = ',value)
                else:
                    print(name,'=',value);
            print(' ')
        """
        """
        print('return list of attribute name value pairs as a dict ');
        list1 = []
        loopvar = 0
        for child in casxmi.getChildElementsFilterBytag(elementType):
            print('******child element =',casxmi.getChildTag(child),'   at index : ',casxmi.getChildIndex(child),'   ******')
            attributes = dict(child.attrib)
            list1.append(attributes)
            "print(attributes)"
            loopvar = loopvar + 1;
        print(list1)
        for listitem in list:
            print(listitem)
            for key, value in listitem.items():
                print(key,value)
        """
if __name__ == '__main__':
    unittest.main()
