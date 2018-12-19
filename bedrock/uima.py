import re as re
import pandas as pd
import spacy
import html
import json
import os
from langdetect import detect
from bedrock.pycas.cas.core import CAS
from bedrock.pycas.type.cas import TypeSystemFactory
from bedrock.pycas.cas.writer import XmiWriter
from bedrock.prelabel.findpattern import findpattern

from bedrock.pycas.cas.writer.CSVConverter import CSVConverter
from bedrock.pycas.cas.core.CasFactory import CasFactory

class Ubertext:

    # TODO: additional constructor with string
    # TODO: wide format, flat  export_flat for ML learning

    def __init__(self, file_path=None, typesysXML_path=None, text=None):
        """ constructor: text (raw format)
                         file_path to text (raw format)
                         path to UIMA_xmi, typesysXML
                    """
        print(file_path)

        # members to keep tokens, annotations and relations
        self.token_df = pd.DataFrame(columns=['doc_id',  'sent_id', 'token_id', 'text', 'begin', 'end',
                                              'is_sent_start', 'pos', 'dep'])
        self.anno_df = pd.DataFrame(columns=['doc_id', 'anno_id', 'token_id', 'begin', 'end', 'layer', 'feature', 'class'])
        self.rel_df = pd.DataFrame(columns=['doc_id', 'gov_anno_id', 'dep_anno_id', 'layer', 'role'])

        # TODO method call with return to text_raw
        self.text_raw = ''

        # UIMA xmi format
        if str(file_path).endswith("xmi"):

            if typesysXML_path is None:
                raise ValueError('typesysXML path missing')

            casXMI = self.read_file_to_string(file_path)
            typesysXML = self.read_file_to_string(typesysXML_path)
            cas = CasFactory().buildCASfromStrings(casXMI, typesysXML)
            self.text_preproc = cas.documentText
            self.language = detect(self.text_preproc)

            self.token_df, self.anno_df, self.relation_df = CSVConverter().writeToCSV(cas)
        else:
            if text is not None:
                self.text_raw=text
            else:
                self.file_path = file_path
                self.text_raw = self.__set_text_from_report_file_path(file_path)

            self.text_preproc = self.__preprocess()
            self.language = detect(self.text_preproc)
            nlp = spacy.load(self.language)
            self.spacy_doc = nlp( self.text_preproc)

            # TODO@RITA: add pos tags, dependency tags output spacy
            tmp_token_df = pd.DataFrame(
                [(token.text, token.idx, token.idx + len(token.text), token.is_sent_start, token_id)
                for token_id, token in enumerate(self.spacy_doc)],
                columns=['text', 'beg', 'end', 'is_sent_start', 'id'] )
            self.token_df = self.token_df.append(tmp_token_df, ignore_index=True)

    def build_cas_from_spacy(self, typesystem_filepath):
        if self.spacy_doc.is_parsed is False:
            raise ValueError('spaCy doc must be parsed')

        # TODO: set as function parameter
        type_system_factory = TypeSystemFactory.TypeSystemFactory()
        type_system = type_system_factory.readTypeSystem(typesystem_filepath)
        cas = CAS.CAS(type_system)
        cas.documentText = self.text_preproc
        cas.sofaMimeType = 'text'

        sentence_type = 'de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Sentence'
        token_type = 'de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token'

        doc_len = len(self.text_preproc)

        # escaped version of tokens TODO: check whether necessary
        token_df_out = self.token_df
        sentence_list = pd.DataFrame()

        token_nr = len(token_df_out)
        for t in range(0, token_nr):
            fs_token = cas.createAnnotation(token_type, {'begin': token_df_out['beg'][t], 'end': token_df_out['end'][t]})
            cas.addToIndex(fs_token)
            if token_df_out['is_sent_start'][t] is True or t == 0:
                sentence_list = sentence_list.append(token_df_out.iloc[t], ignore_index=True)

        for s in range(0, len(sentence_list)):
            if s < len(sentence_list)-1:
                end = int(sentence_list['beg'][s+1].astype(int)-1)-1
            else:
                end = doc_len
            fs_sentence = cas.createAnnotation(sentence_type, {
                'begin': int(sentence_list['beg'][s].astype(int)),
                'end': end
            })
            cas.addToIndex(fs_sentence)
        return cas

    def add_tnm_prelabel_to_cas(self, cas, rel_pattern_filepath):
        abspath = os.path.dirname(__file__)
        path = os.path.join(abspath, rel_pattern_filepath)
        custom_type = 'webanno.custom.Tumor'
        with open(path, 'r') as f:
            pattern_json = json.load(f)
        vec, match = findpattern(pattern_json['TNM']['all']['regex'], self.text_preproc)
        anno = {
            'begin': vec[0][0],
            'end': vec[0][1],
            pattern_json['TNM']['all']['xmi_property']: pattern_json['TNM']['all']['label']
        }
        fs_custom_annotation = cas.createAnnotation(custom_type, anno)
        cas.addToIndex(fs_custom_annotation)
        return cas

    def __set_text_from_report_file_path(self, file_path):
        with open(file_path, 'r') as f:
            text_raw = f.read()
        return text_raw

    def save(self, file_path):
        import bedrock.common
        bedrock.common.save_pickle(self, file_path)

    def __escape(self, string_unescap):
        """ argument string_unescap: string xml unescaped
            returns string_escape: xml escaped and
                    pos_map: map for conversion of position of the two strings
            """
        string_escap = string_unescap
        char_inserts = []
        escape_dict = pd.DataFrame({'char_esc': ['&amp;', '&lt;', '&gt;', '&quot;', '&apos;'],
                                    'char_unesc': ['&', '<', '>', '"', '\'']})
        escape_dict['len_dif'] = escape_dict['char_esc'].str.len() - escape_dict['char_unesc'].str.len()

        for j in range(len(escape_dict)):
            string_escap = string_escap.replace(escape_dict['char_unesc'][j], escape_dict['char_esc'][j])
            pos = [match.start() for match in re.finditer(re.escape(escape_dict['char_unesc'][j]), string_unescap)]
            char_inserts.extend(pos * escape_dict['len_dif'][j])

        char_inserts.extend(list(range(len(string_unescap) +1)))
        char_inserts.sort()
        assert len(list(range(len(string_escap) +1))) == len(char_inserts)

        # range including end
        pos_map = pd.DataFrame({'pos_esc': list(range(len(string_escap)+1)), 'pos_unesc': char_inserts})
        pos_map['pos_unesc_uni'] = pos_map['pos_unesc']
        # issue: fill in 'nan' will convert to object but need integer
        # TODO: change required, not a good solution
        pos_map['pos_unesc_uni'][pos_map['pos_unesc_uni'] == pos_map['pos_unesc_uni'].shift(1)] = -99

        return string_escap, pos_map

    def __preprocess(self):
        """ argument text_raw: string
            returns text_proproc: processed string in utf_8 format, escaped
            """
        # preprocess such that webanno and spacy text the same, no changes in Webanno
        # side effect: loose structure of report (newline)

        text_preproc = self.text_raw
        # text_preproc = text_raw

        # TODO: verify with export Webanno
        # utf-8 encoding
        text_preproc.strip('"')
        text_preproc = text_preproc.replace("\n", " ")
        text_preproc = text_preproc.replace("<br>", "\n")
        text_preproc = ' '.join(filter(len, text_preproc.split(' ')))
        text_preproc = html.unescape(text_preproc)
        return text_preproc


    def read_file_to_string(self, file_path):
        with open(file_path) as f:
            s = f.read()
        return s


    def write_csv(self, file_path):
        """ write csv file, one line per token includings annotations

            assuming for each token only 1 annotation per feature.class
        """
        self.anno_df['col_pivot'] =  self.anno_df['layer'] + "." + self.anno_df['feature']
        self.token_df.set_index('token_id')
        t1 = self.anno_df.pivot(index='token_id', values='class' ,
                            columns='col_pivot' )
        t2 = self.token_df.merge(t1, left_on='token_id', right_index=True, how = 'left')
        t2.to_csv(file_path, sep="\t")


def load_ubertext(file_path):
    import bedrock.common
    return bedrock.common.load_pickle(file_path)


if __name__ == '__main__':

    #file_dir = "/home/achermannr/nlp_local/data/iter1/"

    file_dir = '/home/marko/projects/openmednlp/training_development/'
    file_name = '2051460_5616.txt'
    spacy_model = '/home/achermannr/nlp_local/library/de_core_news_sm-2.0.0/de_core_news_sm/de_core_news_sm-2.0.0'

    utxt = Ubertext(file_dir + file_name)
    cas = utxt.build_cas_from_spacy('/home/marko/projects/openmednlp/typesystem.xml')
    cas = utxt.add_tnm_prelabel_to_cas(cas, "prelabel/patterns.json")
    xmi_writer = XmiWriter.XmiWriter()
    xmi_writer.write(cas, '/home/marko/test.xmi')

    test_path = "/home/achermannr/nlp_local/data/export/"
    file_xmi = test_path + "2051460_5616.xmi"
    file_type_syst = test_path + "typesystem.xml"

    utx = Ubertext(file_path=file_xmi, typesysXML_path=file_type_syst )
    utx.write_csv("/home/achermannr/nlp_local/data/export/xxx")

    #utx.persist_json(file_dir + file_names[i].replace('.txt', '.json'))

        #find last name write table with 3 words before and last
        #a=utx.token_df['id'][utx.token_df['text'].str.contains('Tumor')].astype(int)
        #df=pd.DataFrame()

        # for j in range(0,len(a)):
        #     tmp = utx.token_df['text'][a.iloc[j]-3:a.iloc[j] + 3].to_frame()
        #     tmp.columns=["a", "b", "c", "d", "e", "f", "g"]
        #     df=df.append(tmp, ignore_index=True)
        #
        # df.to_csv('/home/achermannr/Temp/' + file_names[i] + '.csv', sep="\t")