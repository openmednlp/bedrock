import unittest2 as unittest

from bedrock.utils.CSVWriter import CSVWriter
from pycas.cas.core.CasFactory import CasFactory



class TestCSVWriterMethods(unittest.TestCase):

    def test_CSVConversion(self):
        test_path = "/home/achermannr/nlp_local/data/export/"
        file_xmi = test_path + "2051460_5616.xmi"
        file_type_syst = test_path + "typesystem.xml"

        casXMI = readFileToString(file_xmi)

        typesysXML = readFileToString(file_type_syst)
        cas = CasFactory().buildCASfromStrings(casXMI, typesysXML)

        token_csv, UIMA_csv = CSVWriter().writeToCSV(cas)

        #to do: remove " from annotation, sent_id / token_id consecutively numbered
        # remove some columns, add meta data doc unique number etc.
        token_csv.to_csv(file_xmi.replace('xmi', 'csv'), sep="\t", index=False)

def readFileToString(path):
    with open(path) as f:
        s = f.read()
    return s

if __name__ == '__main__':
    unittest.main()


