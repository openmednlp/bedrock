import re as re
import pandas as pd
import spacy
import html
import json
import os
import numpy as np
from langdetect import detect
from bedrock.pycas.cas.core import CAS
from bedrock.pycas.type.cas import TypeSystemFactory
from bedrock.pycas.cas.writer import XmiWriter
from bedrock.prelabel.findpattern import findpattern
from bedrock.pycas.cas.core.CasFactory import CasFactory


#to replace for escape with html

from xml.sax.saxutils import quoteattr

from bedrock.pycas.cas.writer.CAStoDf import CAStoDf



class Ubertext:

    # TODO: wide format, flat  export_flat for ML learning

    def __init__(self, file_path=None, typesysXML_path=None, text=None):
        """ constructor: text (raw format)
                         file_path to text (raw format)
                         path to UIMA_xmi, typesysXML
                    """
        #TODO remove
        spacy_model = '/home/achermannr/nlp_local/library/de_core_news_sm-2.0.0/de_core_news_sm/de_core_news_sm-2.0.0'

        print(file_path)

        # members to keep tokens, annotations and relations
        self.token_df = pd.DataFrame(columns=['doc_id',  'sent_id', 'token_id', 'text', 'begin', 'end',
                                              'is_sent_start', 'pos', 'dep'])
        self.anno_df = pd.DataFrame(columns=['doc_id', 'anno_id', 'token_id', 'begin', 'end', 'layer', 'feature', 'class'])
        self.rel_df = pd.DataFrame(columns=['doc_id', 'gov_anno_id', 'dep_anno_id', 'layer', 'role'])
        self.cas = None

        # UIMA xmi format
        if str(file_path).endswith("xmi"):

            if typesysXML_path is None:
                raise ValueError('typesysXML path missing')

            casXMI = self.__read_file_to_string(file_path)
            typesysXML = self.__read_file_to_string(typesysXML_path)

            self.cas = CasFactory().buildCASfromStrings(casXMI, typesysXML)

            self.text_preproc = cas.documentText
            self.text_raw = cas.documentText
            self.language = detect(self.text_preproc) # TODO: why do we get 'en' although 'de'
            self.language = 'de'
            self.token_df, self.anno_df, self.relation_df = CAStoDf().toDf(cas)
        else:
            if text is not None:
                self.text_raw=text
            else:
                self.file_path = file_path
                self.text_raw = self.__read_file_to_string(file_path)

            self.text_preproc = self.__preprocess()
            self.language = detect(self.text_preproc)  # TODO: why do we get 'en' although 'de'
            self.language = 'de'

            #TODO @ RITA: change again
            #nlp = spacy.load(self.language)
            nlp = spacy.load(spacy_model)

            self.spacy_doc = nlp( self.text_preproc)

            #TODO@RITA: add pos tags, dependency tags output spacy
            tmp_token_df = pd.DataFrame(
                [(token.text, token.idx, token.idx + len(token.text), token.is_sent_start, token_id)
                for token_id, token in enumerate(self.spacy_doc)],
                columns=['text', 'beg', 'end', 'is_sent_start', 'id'] )
            self.token_df = self.token_df.append(tmp_token_df, ignore_index=True)

    def set_cas_from_spacy(self, typesystem_filepath):
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
            fs_token = cas.createAnnotation(token_type, {
                'begin': int(token_df_out['beg'][t]),
                'end': int(token_df_out['end'][t])
            })
            cas.addToIndex(fs_token)
            if token_df_out['is_sent_start'][t] is True or t == 0:
                sentence_list = sentence_list.append(token_df_out.iloc[t], ignore_index=True)

        for s in range(0, len(sentence_list)):
            if s < len(sentence_list)-1:
                end = int(sentence_list['beg'][s+1].astype(int)-1) #-1
            else:
                end = doc_len
            fs_sentence = cas.createAnnotation(sentence_type, {
                'begin': int(sentence_list['beg'][s].astype(int)),
                'end': end
            })
            cas.addToIndex(fs_sentence)
        self.cas = cas

    def add_regex_label_to_cas(self, rel_pattern_filepath):
        abspath = os.path.dirname(__file__)
        path = os.path.join(abspath, rel_pattern_filepath)
        custom_type = 'webanno.custom.Tumor'
        with open(path, 'r') as f:
            pattern_json = json.load(f)

        for key1, value in pattern_json.items():
            for key2, value2 in value.items():
                vec, match = findpattern(str(value2['regex']), self.text_preproc)

                for v in vec:
                    anno = {
                        'begin': v[0],
                        'end': v[1],
                        value2['xmi_property']: value2['tag_name']
                    }
                    fs_custom_annotation = self.cas.createAnnotation(custom_type, anno)
                    self.cas.addToIndex(fs_custom_annotation)

        #update internal members
        self.token_df, self.anno_df, self.relation_df = CAStoDf().toDf(self.cas)

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


    def __read_file_to_string(self, file_path):
        with open(file_path) as f:
            s = f.read()
        return s


    def write_csv(self, file_path):
        """ write csv file, one line per token including annotations

            assuming for each token only 1 annotation per feature.class
        """
        #TODO replace
        self.token_df.set_index('token_id')

        if self.anno_df.empty == False:
            self.anno_df['col_pivot'] = self.anno_df['layer'] + "." + self.anno_df['feature'] + "." + self.anno_df['class']
            t1 = self.anno_df.pivot(index='token_id', values='class',
                            columns='col_pivot')
            t2 = self.token_df.merge(t1, left_on='token_id', right_index=True, how = 'left')
            t2.to_csv(file_path, sep="\t")
        else :
            self.token_df.to_csv(file_path, sep="\t")

def load_ubertext(file_path):
    import bedrock.common
    return bedrock.common.load_pickle(file_path)




