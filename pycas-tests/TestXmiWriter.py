import unittest2 as unittest

import xml.etree.ElementTree as ET

from pycas.cas.writer.XmiWriter import XmiWriter
from pycas.cas.core.CasFactory import CasFactory

class TestXmiWriterMethods(unittest.TestCase):

    def test_readingOwnWrites(self):
        casXMI = readFileToString('tests/testing_data/document3.txt.xmi')
        typesysXML = readFileToString('tests/testing_data/typesystem.xml')
        cas = CasFactory().buildCASfromStrings(casXMI, typesysXML)

        writtenCas = XmiWriter().writeToString(cas)

        expectedXML = ET.fromstring(casXMI)
        actualXML = ET.fromstring(writtenCas)
        self.assertXMLEqual(expectedXML, actualXML)

    def test_writingTextWithXMLCharacters(self):
        casXMI = readFileToString('tests/testing_data/document3_xml_characters.txt.xmi')
        typesysXML = readFileToString('tests/testing_data/typesystem.xml')
        cas = CasFactory().buildCASfromStrings(casXMI, typesysXML)

        writtenCas = XmiWriter().writeToString(cas)

        expectedXML = ET.fromstring(casXMI)
        actualXML = ET.fromstring(writtenCas)
        self.assertXMLEqual(expectedXML, actualXML)

    def assertXMLEqual(self, e1, e2):
        self.assertEqual(e1.tag, e2.tag, 'Expected {0}, was {1}'.format(e1.tag, e2.tag))
        self.assertEqual(e1.attrib, e2.attrib, 'Expected {0}, was {1}'.format(e1.attrib, e2.attrib))
        self.assertEqual(len(e1), len(e2), 'Expected len {0}, was len {1}'.format(len(e1), len(e2)))
        
        for c1, c2 in zip(e1, e2):
            self.assertXMLEqual(c1, c2)

def readFileToString(path):
    with open(path) as f:
        s = f.read()
    return s

if __name__ == '__main__':
    unittest.main()


