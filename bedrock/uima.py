import re as re
import pandas as pd
import spacy
from xml.sax import saxutils


import json
import os
from langdetect import detect
from bedrock.pycas.cas.core import CAS
from bedrock.pycas.type.cas import TypeSystemFactory
from bedrock.prelabel.findpattern import findpattern
from bedrock.pycas.cas.core.CasFactory import CasFactory
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from fuzzysearch import find_near_matches

from xml.sax.saxutils import quoteattr

from bedrock.pycas.cas.writer.CAStoDf import CAStoDf



class Ubertext:

    # TODO: wide format, flat  export_flat for ML learning

    def __init__(self, spacy_model_path=None, file_path=None, typesysXML_path=None, text=None):

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

            self.text_preproc = self.cas.documentText
            self.text_raw = self.cas.documentText
            self.language = detect(self.text_preproc) # TODO: why do we get 'en' although 'de'
            self.language = 'de'
            self.token_df, self.anno_df, self.relation_df = CAStoDf().toDf(self.cas)
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
            nlp = spacy.load(spacy_model_path)
            nlp.add_pipe(self.set_custom_boundaries, before='parser')

            self.spacy_doc = nlp( self.text_preproc)

            #TODO@RITA: add pos tags, dependency tags output spacy
            tmp_token_df = pd.DataFrame(
                [(token.text, token.idx, token.idx + len(token.text),
                  token.is_sent_start, token.pos_,token.dep_, token_id,
                 #"{0}-{1}".format(token.ent_iob_, token.ent_type_) if token.ent_iob_ != 'O' else token.ent_iob_,
                  token.head.i)
                for token_id, token in enumerate(self.spacy_doc)],
                columns=['text', 'beg', 'end', 'is_sent_start', 'pos', 'dep', 'id', 'gov_id'])
            self.token_df = self.token_df.append(tmp_token_df, ignore_index = True)

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
        pos_type = 'de.tudarmstadt.ukp.dkpro.core.api.lexmorph.type.pos.POS'
        dependency_type = 'de.tudarmstadt.ukp.dkpro.core.api.syntax.type.dependency.Dependency'
        flavor_tag = "de.tudarmstadt.ukp.dkpro.core.api.syntax.type.dependency.Dependency"

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

            fs_anno = cas.createAnnotation(pos_type, {
                'begin': int(token_df_out['beg'][t]),
                'end': int(token_df_out['end'][t]),
                'PosValue': token_df_out['pos'][t]
            })
            cas.addToIndex(fs_anno)

            #TODO add dependencies to cas
            '''
            aFeature = Feature('de.tudarmstadt.ukp.dkpro.core.api.syntax.type.dependency.Dependency', 'DependencyType')
            aFeature.listval =  {'Governor': token_df_out['gov_id'][t],
                                'Dependent': token_df_out['id'][t],
                                'DependencyType': token_df_out['dep'][t],
                                'flavor': 'basic'}
            fs_dep = cas.createAnnotation(dependency_type, {
                'begin': int(token_df_out['beg'][t]),
                'end': int(token_df_out['end'][t])},
                 aFeature
            )
            cas.addToIndex(fs_dep)
            '''
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
        # uima, self.token_df, self.anno_df, self.relation_df = CAStoDf().toDf(self.cas)

    def add_dictionary_label_to_cas(self, icd_o_definition_file_path):
        # start with an naïve approach with fuzzy token_set
        dictionary = pd.read_csv(icd_o_definition_file_path, sep='\t')
        dictionary = dictionary[dictionary['languageCode'] == 'de']
        dictionary = dictionary.drop(columns=['effectiveTime', 'languageCode', 'Source'])

        for sent in self.spacy_doc.sents:
            self.__fuzzy_extract(sent, dictionary['term'], dictionary['referencedComponentId'], 86, len(sent))

    def __fuzzy_extract(self, sent, queries, codes, threshold, limit):
        '''fuzzy matches 'qs' in 'ls' and returns list of
        tuples of (word,index)
        '''
        custom_type = 'webanno.custom.Tumor'
        for word, _, _ in process.extractBests(sent.text, queries, scorer=fuzz.token_set_ratio, score_cutoff=threshold, limit=limit):
            matches = find_near_matches(word, sent.text, max_l_dist=2)
            index = queries[queries == word].index[0]
            code = codes[index]
            for match in matches:
                dada = word[match.start:match.end]
                anno = {
                    'begin': sent.start_char + match.start,
                    'end': sent.end_char + match.end,
                    'Morphology': code
                }
                fs_custom_annotation = self.cas.createAnnotation(custom_type, anno)
                self.cas.addToIndex(fs_custom_annotation)

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
        text_preproc = saxutils.unescape(text_preproc)
        return text_preproc


    def __read_file_to_string(self, file_path):
        with open(file_path) as f:
            s = f.read()
        return s

    def set_custom_boundaries(self, doc):
        for token in doc[:-1]:
            if token.text == ':':
                doc[token.i + 1].is_sent_start = False
        return doc


def load_ubertext(file_path):
    import bedrock.common
    return bedrock.common.load_pickle(file_path)




