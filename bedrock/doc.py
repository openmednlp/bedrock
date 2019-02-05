import re as re
import pandas as pd
import spacy
from xml.sax import saxutils

import json
import os
import numpy as np
from langdetect import detect
from bedrock.pycas.cas.core import CAS
from bedrock.pycas.type.cas import TypeSystemFactory
from bedrock.pycas.cas.writer import XmiWriter
from bedrock.prelabel.findpattern import findpattern
from bedrock.pycas.cas.core.CasFactory import CasFactory
from bedrock.pycas.type.cas.Feature import Feature
from bedrock.pycas.cas.core.FeatureStructure import FeatureStructure
from bedrock.pycas.cas.writer import XmiWriter

#to replace for escape with html

from xml.sax.saxutils import quoteattr

from bedrock.pycas.cas.writer.CAStoDf import CAStoDf



class Doc:

    def __init__(self, file_path=None, typesysXML_path=None, text=None):
        """ constructor: text (raw format)
                         file_path to text (raw format)
                         path to UIMA_xmi, typesysXML
                    """

        print(file_path)

        # members to keep tokens, annotations and relations
        self.token_df = pd.DataFrame(columns=['doc_id',  'sent_id', 'token_id', 'text', 'beg', 'end',
                                              'is_sent_start', 'pos', 'dep'])
        self.anno_df = pd.DataFrame(columns=['doc_id', 'sofa_id', 'token_id', 'begin', 'end', 'layer', 'feature', 'class'])
        self.rel_df = pd.DataFrame(columns=['doc_id','sofa_id','gov_anno_id', 'dep_anno_id', 'layer', 'role'])

        #counter for sujectOfAnalysis, unique for all items within document
        self.sofa_id = 0

        # if UIMA xmi format
        if str(file_path).endswith("xmi"):

            if typesysXML_path is None:
                raise ValueError('typesysXML path missing')

            casXMI = self.__read_file_to_string(file_path)
            typesysXML = self.__read_file_to_string(typesysXML_path)

            self.cas = CasFactory().buildCASfromStrings(casXMI, typesysXML)

            self.text_preproc = cas.documentText
            self.text_raw = cas.documentText
            self.language = detect(self.text_preproc)
            self.language = 'de'
            self.token_df, self.anno_df, self.relation_df = CAStoDf().toDf(cas)
        else:
            if text is not None:
                self.text_raw=text
            else:
                self.file_path = file_path
                self.text_raw = self.__read_file_to_string(file_path)

            self.text_preproc = self.__preprocess()
            self.language = detect(self.text_preproc)
            self.language = 'de'
            self.__set_doc_with_spacy()


    def __set_doc_with_spacy(self):

        #TODO: move outside, why do we get 'en' although 'de' when initialized self.lanuguage
        spacy_model = '/home/achermannr/nlp_local/library/de_core_news_sm-2.0.0/de_core_news_sm/de_core_news_sm-2.0.0'

        nlp = spacy.load(spacy_model)
        nlp.add_pipe(self.set_custom_boundaries, before='parser')

        spacy_doc = nlp(self.text_preproc)

        token_df = pd.DataFrame(
            [(token.text, token.idx, token.idx + len(token.text),
              token.is_sent_start, token.pos_, token.dep_, token_id,
              "{0}-{1}".format(token.ent_iob_, token.ent_type_) if token.ent_iob_ != 'O' else token.ent_iob_,
              token.head.i)
             for token_id, token in enumerate(spacy_doc)],
                columns=['text', 'beg', 'end', 'is_sent_start', 'pos', 'dep', 'id', 'ent','gov_id'])
        self.token_df = token_df

        # tokens
        self.anno_df = token_df[['beg', 'end', 'id']]
        self.anno_df.loc[:,'layer'] = 'token'
        self.anno_df.loc[:,'feature'] = 'token'
        self.anno_df.loc[:,'class'] = token_df['id']
        self.anno_df.loc[:,'sofa_id'] = list(range(self.sofa_id, self.sofa_id + self.anno_df.shape[0]))
        self.sofa_id += self.anno_df.shape[0]


        #POS annotations
        pos_anno_df = token_df[['beg', 'end', 'id']]
        pos_anno_df.loc[:,'layer'] = 'pos'
        pos_anno_df.loc[:,'feature'] = 'pos'
        pos_anno_df.loc[:,'class'] = token_df['pos']
        pos_anno_df.loc[:,'sofa_id'] = list(range(self.sofa_id, self.sofa_id + pos_anno_df.shape[0]))
        self.sofa_id += pos_anno_df.shape[0]
        self.anno_df = self.anno_df.append(pos_anno_df, ignore_index=True)


        #sentence annotations
        sent_start = token_df['is_sent_start'] == True
        sent_start[0] = True

        sentence_anno = pd.DataFrame(token_df[sent_start]['beg'].astype(int))
        sentence_anno.loc[:,'end'] = sentence_anno['beg'].shift(-1).fillna(len(self.text_preproc)).astype(int)-1
        sentence_anno.loc[:,'layer'] = 'sentence'
        sentence_anno.loc[:,'feature'] = 'sentence'
        sentence_anno.loc[:,'class'] = list(range(sentence_anno.shape[0]))
        sentence_anno.loc[:,'sofa_id'] = list(range(self.sofa_id, self.sofa_id + sentence_anno.shape[0]))

        self.sofa_id += sentence_anno.shape[0]
        self.anno_df = self.anno_df.append(sentence_anno, ignore_index=True)

        #dependencies
        self.rel_df = token_df[['beg', 'end', 'id']]
        self.rel_df.loc[:, 'layer'] = 'dependency'
        self.rel_df.loc[:, 'feature'] = 'dependency'
        self.rel_df.loc[:, 'class'] = token_df['dep']
        self.rel_df.loc[:, 'sofa_id'] = list(range(self.sofa_id, self.sofa_id + pos_anno_df.shape[0]))
        self.rel_df.loc[:, 'dep_id'] = token_df['id']
        self.rel_df.loc[:, 'gov_id'] = token_df['gov_id']
        self.rel_df.loc[:, 'sofa_id'] = list(range(self.sofa_id, self.sofa_id + self.rel_df.shape[0]))
        self.sofa_id += self.rel_df.shape[0]

    def get_cas(self, typesystem_filepath):

        if self.token_df.empty:
            raise ValueError('token df empty in Doc.get_cas()')

        type_system_factory = TypeSystemFactory.TypeSystemFactory()
        type_system = type_system_factory.readTypeSystem(typesystem_filepath)
        cas = CAS.CAS(type_system)
        cas.documentText = self.text_preproc
        cas.sofaMimeType = 'text'

        sentence_type = 'de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Sentence'
        token_type = 'de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token'
        pos_type = 'de.tudarmstadt.ukp.dkpro.core.api.lexmorph.type.pos.POS'
        dependency_type = 'de.tudarmstadt.ukp.dkpro.core.api.syntax.type.dependency.Dependency'
        flavor_tag = 'de.tudarmstadt.ukp.dkpro.core.api.syntax.type.dependency.Dependency'
        custom_type = 'webanno.custom.Tumor'

        for t in range(0, self.anno_df.shape[0]):

            layer = self.anno_df['layer'][t]
            if layer == 'token':
                fs_anno = cas.createAnnotation(token_type, {
                    'begin': int(self.anno_df['beg'][t]),
                    'end': int(self.anno_df['end'][t])

                })
            elif layer == 'pos':
                fs_anno = cas.createAnnotation(pos_type, {
                    'begin': int(self.anno_df['beg'][t]),
                    'end': int(self.anno_df['end'][t]),
                    'PosValue': self.anno_df['class'][t]
                })
            elif layer.startswith('custom') :
                fs_anno = cas.createAnnotation(custom_type,{
                    'begin':  int(self.anno_df['beg'][t]),
                    'end': int(self.anno_df['end'][t]),
                    self.anno_df['feature'][t]: self.anno_df['class'][t]
                })
            elif layer == 'sentence':
                fs_anno = cas.createAnnotation(sentence_type, {
                    'begin': int(self.anno_df['beg'][t]),
                    'end': int(self.anno_df['end'][t])
                })
            else:
                print(str(self.anno_df['sofa_id'][t]) + ' unknown annotation')

            if fs_anno is not None:
                cas.addToIndex(fs_anno)

        # TODO add dependencies to cas
        # < dependency: Dependency
        # xmi: id = "6501"
        # sofa = "1"
        # begin = "60"
        # end = "63"
        # Governor = "78"
        # Dependent = "92"
        # DependencyType = "acl"
        # flavor = "basic" / >
        return cas

    def add_regex_label(self, rel_pattern_filepath):
        abspath = os.path.dirname(__file__)
        path = os.path.join(abspath, rel_pattern_filepath)
        with open(path, 'r') as f:
            pattern_json = json.load(f)

        for key1, value in pattern_json.items():
            for key2, value2 in value.items():
                vec, match = findpattern(str(value2['regex']), self.text_preproc)

                #todo list and then convert at end instead of df
                for v in vec:
                    self.anno_df=self.anno_df.append({
                        'beg': int(v[0]),
                        'end': int(v[1]),
                        'layer': 'custom',
                        'feature': value2['xmi_property'],
                        'class': value2['tag_name'],
                        'sofa_id': self.sofa_id
                    }, ignore_index=True)
                    self.sofa_id += 1

    def remove_annotation(self, sofa_id_list):
        rm = self.anno_df['sofa_id'].isin(sofa_id_list)
        if sum(rm) > 0:
           self.anno_df = self.anno_df[rm==False]

    def remove_relation(self, sofa_id_list):
        rm = self.rel_df['sofa_id'].isin(sofa_id_list)
        if sum(rm) > 0:
           self.rel_df = self.rel_df[rm==False]

    def save(self, file_path):
        import bedrock.common
        bedrock.common.save_pickle(self, file_path)

    def __escape(self, string_unescap):
        """ argument string_unescap: string xml unescaped
            returns string_escape: xml escaped and
                    pos_map: map for conversion of position of the two strings
            """
        #todo required?
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
        # side effect: lose structure of report (newline)

        text_preproc = self.text_raw


        # utf-8 encoding
        text_preproc.strip('"')
        text_preproc = text_preproc.replace("\n", " ")
        text_preproc = text_preproc.replace("<br>", "\n")
        text_preproc = ' '.join(filter(len, text_preproc.split(' ')))
        text_preproc = saxutils.unescape(text_preproc)
        return text_preproc


    def __read_file_to_string(self, file_path):
        with open(file_path) as f:
            s = f.read()
        return s

    def set_custom_boundaries(self, doc):
        '''function for spacy: sentence bounderies not :'''
        #Todo move outside doc class
        for token in doc[:-1]:
            if token.text == ':':
                doc[token.i + 1].is_sent_start = False
        return doc

    def write_UIMA_xmi(self, file_name, typesystem_filepath):
        cas = self.get_cas(typesystem_filepath)
        xmi_writer = XmiWriter.XmiWriter()
        xmi_writer.write(cas, file_name)

def load_ubertext(file_path):
    import bedrock.common
    return bedrock.common.load_pickle(file_path)




