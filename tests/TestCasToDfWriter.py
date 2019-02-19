import unittest2 as unittest

import os
from bedrock.pycas.cas.core.CasFactory import CasFactory
from bedrock.utils.CAS2DataFrameConverter import CAS2DataFrameConverter


class TestCAStoDFWriterMethods(unittest.TestCase):

    def test_CSVConversion(self):

        file_input_dir = "../tests/data/input/"
        file_output_dir = "../tests/data/output/"
        file_type_syst = file_input_dir + "typesystem.xml"
        file_names = [f for f in os.listdir(file_input_dir) if f.endswith('.xmi')]

        for file in range(0, len(file_names)):
            with open(file_input_dir + file_names[file], 'r') as f:
                casXMI = readFileToString(f.name)
                typesysXML = readFileToString(file_type_syst)
                cas = CasFactory().buildCASfromStrings(casXMI, typesysXML)

                uima_df, token_df, anno_df, rel_df = CAS2DataFrameConverter().toDf(cas)
                uima_df.to_csv(file_output_dir + file_names[file].replace('.xmi', '_uima.csv'), sep="\t", index=False)
                anno_df.to_csv(file_output_dir + file_names[file].replace('xmi', '_anno.csv'), sep="\t", index=False)

def readFileToString(path):
    with open(path) as f:
        s = f.read()
    return s

if __name__ == '__main__':
    unittest.main()


