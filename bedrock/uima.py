import json
import spacy
import pandas as pd
import re as re
from langdetect import detect
import html
from pycas.cas.writer.CSVConverter import CSVConverter
from pycas.cas.core.CasFactory import CasFactory


class Ubertext():
    #todo: additional constructor with string
    #todo: wide format, flat  export_flat for ML learning

    def __init__(self, file_path = None, typesysXML_path = None, text = None):
        """ constructor: text (raw format)
                         file_path to text (raw format)
                         path to UIMA_xmi, typesysXML
                    """
        print(file_path)

        #members to keep tokens, annotations and relations
        self.token_df = pd.DataFrame(columns=['doc_id',  'sent_id', 'token_id', 'text', 'begin', 'end',
                                              'is_sent_start', 'pos', 'dep'])
        self.anno_df = pd.DataFrame(columns=['doc_id', 'anno_id', 'token_id', 'begin', 'end', 'layer', 'feature', 'class'])
        self.rel_df = pd.DataFrame(columns=['doc_id', 'gov_anno_id', 'dep_anno_id', 'layer', 'role'])

        self.text_raw = ''

        #UIMA xmi format
        if str(file_path).endswith("xmi"):

            if typesysXML_path == None:
                raise ValueError('typesysXML path missing')

            casXMI = self.read_file_to_string(file_path)
            typesysXML = self.read_file_to_string(typesysXML_path)
            cas = CasFactory().buildCASfromStrings(casXMI, typesysXML)
            self.text_preproc = cas.documentText
            self.language = detect(self.text_preproc)

            self.token_df, self.anno_df, self.relation_df = CSVConverter().writeToCSV(cas)
            print("yes")
        else:
            if text != None:
                self.text_raw=text
            else:
                self.__set_text_from_report(file_path)
                self.file_path = file_path

            self.text_preproc = self.__preprocess()
            self.language = detect(self.text_preproc)

            #todo: external variable spacy_model, should be language
            nlp = spacy.load(spacy_model)

            #always unescaped text otherwise tokenization does not work properly
            self.spacy_doc = nlp( self.text_preproc)

            #todo: add pos tags, dependency tags output spacy
            tmp_token_df = pd.DataFrame(
                [(token.text, token.idx, token.idx + len(token.text), token.is_sent_start, token_id)
                for token_id, token in enumerate(self.spacy_doc)],
                columns=['text', 'beg', 'end', 'is_sent_start', 'id'] )

            self.token_df = self.token_df.append(tmp_token_df, ignore_index=True)


    def create_UIMA_xmi_from_spacy(self, escape=False):

        doc_len = int(0)
        xmi_id = int(13)
        sofa_id = int(12)

        if self.spacy_doc.is_parsed is False:
            raise ValueError('spaCy doc must be parsed')

        #transformation if escaped
        if escape == True:
            #remark position of the token don't need to be changed
            #refer to unescaped string
            text_preproc_write, escape_map = self.__escape(self.text_preproc)
            #doc_len = len(text_preproc_write)

            #transform token positions to escaped string version
            # token_df_out = self.token_df.merge(escape_map[['pos_esc', 'pos_unesc_uni']],
            #                                      how='left', left_on='beg', right_on='pos_unesc_uni')
            # token_df_out.rename(columns={'pos_esc': 'beg_esc'}, inplace=True)
            # token_df_out = token_df_out.merge(escape_map[['pos_esc', 'pos_unesc_uni']],
            #                                      how='left', left_on='end', right_on='pos_unesc_uni')
            # token_df_out.rename(columns={'pos_esc': 'end_esc'}, inplace=True)
            # token_df_out['beg'] = token_df_out['beg_esc']
            # token_df_out['end'] = token_df_out['end_esc']
            #token_df_out = self.token_df
            #doc_len = len(self.text_preproc)
        else:
            text_preproc_write = self.text_preproc

        doc_len = len(self.text_preproc)

        #escaped version of tokens
        #to do: check whether necessary
        token_df_out = self.token_df


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
            '<type2:DocumentMetaData xmi:id="' + str(xmi_id) + '" sofa="' + str(sofa_id) + '" begin="0" end="' + str(doc_len) + '" ',
            'language="x-unspecified" documentTitle="None" documentId="spacy nlp"',
            'documentUri ="' + self.file_path + '"',
            'collectionId = "' + self.file_path + '"',
            'documentBaseUri = "' + self.file_path + '"',
            'isLastSegment = "false"/>'])
        xmi_id += 1

        sofa = '<cas:Sofa xmi:id="{sofa}" sofaNum="' + str(xmi_id) + '" sofaID="_InitialView" mimeType="text" sofaString="{sofa_string}"/>'

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

        token_nr =len(token_df_out)
        for t in range(0, token_nr):
            tmp = {'id': xmi_id, 'sofa': sofa_id, 'begin': token_df_out['beg'][t],
                   'end': token_df_out['end'][t] }
            rows.append(token.format(**tmp))
            rows.append('\n')
            xmi_id += 1

            if token_df_out['is_sent_start'][t]==True or t==0:
                sentence_list = sentence_list.append(token_df_out.iloc[t], ignore_index=True)


        for s in range(0, len(sentence_list)):
            if s < len(sentence_list)-1:
                tmp ={'id': xmi_id, 'sofa': sofa_id, 'begin': sentence_list['beg'][s].astype(int),
                       'end': sentence_list['beg'][s+1].astype(int)-1 }
            else:
                tmp ={'id': xmi_id, 'sofa': sofa_id, 'begin': sentence_list['beg'][s].astype(int),
                       'end': doc_len }
            xmi_id += 1
            rows.append(sentence.format(**tmp))
            rows.append('\n')

        #to do change, hard coded start xmi_id
        tmp = {'sofa': sofa_id, 'member_list': ' '.join([str(xmi_id)
                for xmi_id in range(13, xmi_id)])}

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

        char_inserts.extend(list(range(len(string_unescap) +1)))
        char_inserts.sort()
        assert len(list(range(len(string_escap) +1))) == len(char_inserts)

        #range including end
        pos_map = pd.DataFrame({'pos_esc': list(range(len(string_escap)+1)), 'pos_unesc': char_inserts})
        pos_map['pos_unesc_uni'] = pos_map['pos_unesc']
        #issue: fill in 'nan' will convert to object but need integer
        #todo: change -99 to nan
        pos_map['pos_unesc_uni'][pos_map['pos_unesc_uni'] == pos_map['pos_unesc_uni'].shift(1)] = -99

        return string_escap, pos_map

    def __preprocess(self):
        """ argument text_raw: string
            returns text_proproc: processed string in utf_8 format, escaped

            preprocess such that webanno and spacy text the same, no changes in Webanno
            side effect: lose structure of report (newline)
            """

        text_preproc=self.text_raw


        #todo:  verify with export Webanno
        #utf-8 encoding
        text_preproc.strip('"')
        text_preproc = text_preproc.replace("\n", " ")
        text_preproc = text_preproc.replace("<br>", "\n")
        text_preproc =' '.join( filter( len, text_preproc.split( ' ' ) ))
        text_preproc=html.unescape(text_preproc)

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

    import os as os

    # # file_dir = "/home/achermannr/nlp_local/data/iter1/"
    # file_dir = "/home/achermannr/nlp_local/data/test/"
    #
    # spacy_model = '/home/achermannr/nlp_local/library/de_core_news_sm-2.0.0/de_core_news_sm/de_core_news_sm-2.0.0'
    #
    # file_names = [f for f in os.listdir(file_dir) if f.endswith('.txt')]
    #
    # for i in range(0, len(file_names)):
    #     utx = Ubertext(file_dir + file_names[i])
    #     # utx.create_UIMA_xmi_from_spacy(escape=True)
    #     # to do called twice
    #     if utx.language == 'de':
    #         utx.persist_xmi(file_dir + file_names[i].replace('.txt', '.xmi'), escape=True)



    ###UIMA

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