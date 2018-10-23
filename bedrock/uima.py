import json
import spacy
import pandas as pd
import re as re

class Ubertext():

    def __init__(self, file_path, lang='de'):
        print(file_path)

        self.__set_text_from_report(file_path)
        self.file_path = file_path

        #preprocess such that webanno and spacy text the same, no changes in Webanno
        #side effect: loose structure of report (newline)
        self.text_preproc = self.text_raw
        ###to do:  verify with export Webanno
        self.text_preproc.strip('"')
        #self.text_preproc = self.text_preproc.replace("\n", " ")
        #self.text_preproc =' '.join( filter( len, self.text_preproc.split( ' ' ) ))

        nlp = spacy.load(lang)

        #always unescaped text otherwise tokenization does not work properly
        self.spacy_doc = nlp( self.text_preproc )

        self.token_list_df = pd.DataFrame(
            [(token.text, token.idx, token.idx + len(token.text), token.is_sent_start, token_id)
             for token_id, token in enumerate(self.spacy_doc)],
            columns=['text', 'beg', 'end', 'is_sent_start', 'id'] )


    def create_UIMA_xmi_from_spacy(self, escape=False):

        doc_len = int(0)
        xmi_id = int(0)
        sofa_id = int(12)

        if self.spacy_doc.is_parsed is False:
            raise ValueError('spaCy doc must be parsed')

        #transformation if escaped
        if escape == True:
            text_preproc_write, escape_map = self.__escape(self.text_preproc)
            doc_len = len(text_preproc_write)

            #transform token positions to escaped string version
            token_list_df_out = self.token_list_df.merge(escape_map[['pos_esc', 'pos_unesc_uni']],
                                                 how='left', left_on='beg', right_on='pos_unesc_uni')
            token_list_df_out.rename(index=str, columns={'pos_esc': 'beg_esc'})
            token_list_df_out = self.token_list_df.merge(escape_map[['pos_esc', 'pos_unesc_uni']],
                                                 how='left', left_on='end', right_on='pos_unesc_uni')
            token_list_df_out.rename(index=str, columns={'pos_esc': 'end_esc'})
        else:
            text_preproc_write = self.text_preproc
            doc_len = len(self.text_preproc)
            token_list_df_out = self.token_list_df


        XML_HEADER_ = '<?xml version="1.0" encoding="UTF-8"?>'


        UIMA_XMI_BEGIN_ = ' '.join(
            ['<xmi:XMI',
            'xmlns:pos="http:///de/tudarmstadt/ukp/dkpro/core/api/lexmorph/type/pos.ecore"',
            'xmlns:tcas="http:///uima/tcas.ecore"',
            'xmlns:xmi="http://www.omg.org/XMI"',
            'xmlns:cas="http:///uima/cas.ecore"',
            'xmlns:tweet="http:///de/tudarmstadt/ukp/dkpro/core/api/lexmorph/type/pos/tweet.ecore"',
            'xmlns:morph="http:///de/tudarmstadt/ukp/dkpro/core/api/lexmorph/type/morph.ecore"',
            'xmlns:dependency="http:///de/tudarmstadt/ukp/dkpro/core/api/syntax/type/dependency.ecore"',
            'xmlns:type5="http:///de/tudarmstadt/ukp/dkpro/core/api/semantics/type.ecore"',
            'xmlns:type7="http:///de/tudarmstadt/ukp/dkpro/core/api/transform/type.ecore"',
            'xmlns:type6="http:///de/tudarmstadt/ukp/dkpro/core/api/syntax/type.ecore"',
            'xmlns:type2="http:///de/tudarmstadt/ukp/dkpro/core/api/metadata/type.ecore"',
            'xmlns:type3="http:///de/tudarmstadt/ukp/dkpro/core/api/ner/type.ecore"',
            'xmlns:type4="http:///de/tudarmstadt/ukp/dkpro/core/api/segmentation/type.ecore"',
            'xmlns:type="http:///de/tudarmstadt/ukp/dkpro/core/api/coref/type.ecore"',
            'xmlns:constituent="http:///de/tudarmstadt/ukp/dkpro/core/api/syntax/type/constituent.ecore"',
            'xmlns:chunk="http:///de/tudarmstadt/ukp/dkpro/core/api/syntax/type/chunk.ecore"',
            'xmlns:custom="http:///webanno/custom.ecore"',
            'xmi:version="2.0">'] )

        cas = '<cas:NULL xmi:id="' + str(xmi_id) + '"/>'
        xmi_id += 1


        doc_meta = ' '.join([
            '<type2:DocumentMetaData xmi:id="1" sofa="' + str(sofa_id) + '" begin="0" end="' + str(doc_len) + '" ',
            'language="x-unspecified" documentTitle="None" documentId="spacy nlp"',
            'documentUri ="' + self.file_path + '"',
            'collectionId = "' + self.file_path + '"',
            'documentBaseUri = "' + self.file_path + '"',
            'isLastSegment = "false"/>'])

        sofa = '<cas:Sofa xmi:id="{sofa}" sofaNum="1" sofaID="_InitialView" mimeType="text" sofaString="{sofa_string}"/>'

        token = '<type4:Token xmi:id="{id}" sofa="{sofa}" begin="{begin}" end="{end}"/>'

        sentence = '<type4:Sentence xmi:id="{id}" sofa="{sofa}" begin="{begin}" end="{end}"/>'

        view = '<cas:View sofa="{sofa}" members="{member_list}"/>'

        UIMA_XMI_END = '</xmi:XMI>'

        rows = list()
        rows.append(XML_HEADER_)
        rows.append('\n')
        rows.append(UIMA_XMI_BEGIN_)
        rows.append('\n')
        rows.append(cas)
        rows.append('\n')
        rows.append(doc_meta)
        rows.append('\n')

        sentence_list=pd.DataFrame()

        token_nr =len(token_list_df_out)
        for t in range(0, token_nr):
            tmp = {'id': token_list_df_out['id'][t]+2, 'sofa': sofa_id, 'begin': token_list_df_out['beg'][t],
                   'end': token_list_df_out['end'][t] }
            rows.append(token.format(**tmp))
            rows.append('\n')
            xmi_id +=1
            if token_list_df_out['is_sent_start'][t]==True or t==0:
                sentence_list = sentence_list.append(token_list_df_out.iloc[t], ignore_index=True)

        for s in range(0, len(sentence_list)):
            if s < len(sentence_list)-1:
                tmp ={'id': xmi_id, 'sofa': sofa_id, 'begin': sentence_list['beg'][s].astype(int),
                       'end': sentence_list['beg'][s+1].astype(int)-1 }
            else:
                tmp ={'id': xmi_id, 'sofa': sofa_id, 'begin': sentence_list['beg'][s],
                       'end': doc_len }
            xmi_id += 1
            rows.append(sentence.format(**tmp))
            rows.append('\n')

        tmp = {'sofa': sofa_id, 'member_list': ' '.join([str(xmi_id)
                for xmi_id in range(1, xmi_id)])}

        rows.append(sofa.format(sofa=sofa_id, sofa_string= text_preproc_write))
        rows.append('\n')
        rows.append(view.format(**tmp))
        rows.append('\n')
        rows.append(UIMA_XMI_END)
        rows.append('\n')
        return ''.join(rows)


    def __set_text_from_report(self, file_path):
        with open(file_path, 'r') as f:
            self.text_raw = f.read()

    def __set_json(self, file_path):
        with open(file_path, 'r') as f:
            self.json = json.load(f)

    def __get_text_from_json(self):
        s = self.json['_views']['_InitialView']['DocumentMetaData'][0]['sofa']
        full_text = self.json['_referenced_fss'][str(s)]['sofaString']
        return full_text

    def __repr__(self):
        full_text = self.__get_text_from_json()
        doc_metadata = self.json['_views']['_InitialView']['DocumentMetaData'][0]
        return (
                ' - Short info - \n' +
                '\nTitle: ' + doc_metadata['documentTitle'] +
                '\nId: ' + doc_metadata['documentId'] +
                '\n\nFull string:\n' + full_text
        )

    def persist_xmi(self, file_path, escape=False):
        with open(file_path, 'w') as f:
            f.write(self.create_UIMA_xmi_from_spacy(escape=escape))

    def persist_json(self, file_path):
        with open(file_path, 'w') as f:
            json.dump(self.json, f)

    def save(self, file_path):
        import bedrock.common
        bedrock.common.save_pickle(self, file_path)

    def __get_pairs(self, token_id):
        ref_fss = self.json['_referenced_fss']
        for label in ref_fss():
            print(label)

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

        char_inserts.extend(list(range(len(string_unescap))))
        char_inserts.sort()
        assert len(list(range(len(string_escap)))) == len(char_inserts)

        pos_map = pd.DataFrame({'pos_esc': list(range(len(string_escap))), 'pos_unesc': char_inserts})
        pos_map['pos_unesc_uni'] = pos_map['pos_unesc']
        #issue: fill in 'nan' will convert to object but need integer
        #not accepted change
        pos_map['pos_unesc_uni'][pos_map['pos_unesc_uni'] == pos_map['pos_unesc_uni'].shift(1)] = -99

        return string_escap, pos_map

def load_ubertext(file_path):
    import bedrock.common
    return bedrock.common.load_pickle(file_path)


if __name__ == '__main__':

    import os as os

    #file_dir = '/home/achermannr/drivei_nlp_syn/Pathology/TestLabeling/Test/'
    file_dir = path_out = '/home/achermannr/nlp_local/output/TNM2/'
    spacy_model = '/home/achermannr/nlp_local/library/de_core_news_sm-2.0.0/de_core_news_sm/de_core_news_sm-2.0.0'

    file_names =  [f for f in os.listdir(file_dir) if f.endswith('.txt')]

    for i in range(0, len(file_names)):
        utx = Ubertext(file_dir + file_names[i], lang=spacy_model)
        #utx.create_UIMA_xmi_from_spacy(escape=True)
        ###to do called twice
        utx.persist_xmi( file_dir + file_names[i].replace('.txt', '.xmi'), escape=True)


