import unittest
import os
import bedrock.uima as ubertx
from bedrock.pycas.cas.writer import XmiWriter
from bedrock.pycas.cas.writer.CAStoDf import CAStoDf

class CAStoDF(unittest.TestCase):

    spacy_model = '/home/achermannr/nlp_local/library/de_core_news_sm-2.0.0/de_core_news_sm/de_core_news_sm-2.0.0'

    file_input_dir = 'data/input/'
    file_output_dir = 'data/output/'
    file_type_syst = file_input_dir + "typesystem.xml"
    file_names = [f for f in os.listdir(file_input_dir) if f.endswith('.txt')]

    for file in range(0, len(file_names)):
        with open(file_input_dir + file_names[file], 'r') as f:
            utx = ubertx.Ubertext(f.name, file_type_syst)
            utx.set_cas_from_spacy(file_type_syst)

            utx.add_regex_label_to_cas("prelabel/patterns.json")
            xmi_writer = XmiWriter.XmiWriter()
            xmi_writer.write(utx.cas, file_output_dir + file_names[file].replace('.txt', '.xmi'))

            #write to csv
            uima_df, token_df, anno_df, rel_df = CAStoDf().toDf(utx.cas)
            uima_df.to_csv(file_output_dir + file_names[file].replace('.xmi', '_uima.csv'), sep="\t", index=False)
            anno_df.to_csv(file_output_dir + file_names[file].replace('xmi', '_anno.csv'), sep="\t", index=False)

            print(file_names[file])

if __name__ == '__main__':
    unittest.main()
