import unittest
import os
from bedrock.pycas.cas.writer.CAStoDf import CAStoDf
import bedrock.Doc as bdoc
import spacy as spacy


class CAStoDF(unittest.TestCase):

    spacy_model = '/home/achermannr/nlp_local/library/de_core_news_sm-2.0.0/de_core_news_sm/de_core_news_sm-2.0.0'

    file_input_dir = 'data/input/'
    file_output_dir = 'data/output/'
    file_type_syst = file_input_dir + "typesystem_ex.xml"
    file_names = [f for f in os.listdir(file_input_dir) if f.endswith('.txt')]

    for file in range(0, len(file_names)):
        with open(file_input_dir + file_names[file], 'r') as f:
            doc = bdoc.Doc(f.name, file_type_syst)
            doc.add_regex_label("prelabel/patterns.json")
            doc.write_UIMA_xmi(file_output_dir + file_names[file].replace('.txt', '.xmi'), file_type_syst)

            # write to csv
            uima_df, token_df, anno_df, rel_df = CAStoDf().toDf(doc.get_cas(file_type_syst))
            uima_df.to_csv(file_output_dir + file_names[file].replace('.txt', '_uima.csv'), sep="\t", index=False)

            print(file_names[file])


if __name__ == '__main__':
    unittest.main()
