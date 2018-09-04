import json
import spacy


class Ubertext():

    def __init__(self, file_path, lang='de'):
        print(file_path)

        self.__set_text_from_report(file_path)

        ###if text contains " at befinning or end remove
        #self.text.strip('"')

        nlp = spacy.load(lang)
        self.spacy_doc = nlp(self.text)


        self._XML_HEADER_ = '<?xml version="1.0" encoding="UTF-8"?>'

        ###RA add empty space separator
        self._UIMA_XMI_BEGIN_ = ' '.join(['<xmi:XMI',
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
                                         'xmi:version="2.0">'])

        self.cas = '<cas:NULL xmi:id="0"/>'

        ### To do replace with correct items
        self.doc_meta = ' '.join([
                               '<type2:DocumentMetaData xmi:id="1" sofa="12" begin="0" end="' + str(len(self.spacy_doc.text)) + '" '
                               'language="x-unspecified" documentTitle="None" documentId="spacy"',
                               'documentUri ="' + file_path + '"',
                               'collectionId = "file:/srv/webanno/repository/project/1/document/31/source/"',
                               'documentBaseUri = "file:/srv/webanno/repository/project/1/document/31/source/"',
                               'isLastSegment = "false"/>'])

        self.sofa = '<cas:Sofa xmi:id="{sofa}" sofaNum="1" sofaID="_InitialView" mimeType="text" sofaString="{sofa_string}"/>'

        self.token = '<type4:Token xmi:id="{id}" sofa="{sofa}" begin="{begin}" end="{end}"/>'

        self.sentence = '<type4:Sentence xmi:id="{id}" sofa="{sofa}" begin="{begin}" end="{end}"/>'

        self.view = '<cas:View sofa="{sofa}" members="{member_list}"/>'

        self._UIMA_XMI_END = '</xmi:XMI>'

    def create_xmi_string_from_spacy(self):
        if self.spacy_doc.is_parsed is False:
            raise ValueError('spaCy doc must be parsed')

        rows = list()
        rows.append(self._XML_HEADER_)
        rows.append('\n')
        rows.append(self._UIMA_XMI_BEGIN_)
        rows.append('\n')
        rows.append(self.cas)
        rows.append('\n')
        rows.append(self.doc_meta)
        rows.append('\n')



        sofa = 12 # TODO 'sofa': ???
        tmp = {'sofa': 12, 'sofa_string': self.spacy_doc.text}


        xmi_id  = 2
        for j, sent in enumerate(self.spacy_doc.sents):
            tmp = {'id': xmi_id, 'sofa': sofa, 'begin': sent.start_char, 'end': sent.start_char + len(sent.text)}
            rows.append(self.sentence.format(**tmp))
            rows.append('\n')
            xmi_id+=1
            for i, tok in enumerate(sent):
                tmp = {'id': xmi_id, 'sofa': sofa, 'begin': tok.idx, 'end': tok.idx + tok.__len__()}
                rows.append(self.token.format(**tmp))
                rows.append('\n')
                xmi_id += 1
        tmp = {'sofa': sofa, 'member_list': ' '.join([str(xmi_id) for xmi_id in range(1, xmi_id)])}
        rows.append(self.sofa.format(sofa=sofa, sofa_string=self.spacy_doc.text))
        rows.append('\n')
        rows.append(self.view.format(**tmp))
        rows.append('\n')
        rows.append(self._UIMA_XMI_END)
        rows.append('\n')
        return ''.join(rows)

    def __set_text_from_report(self, file_path):
        with open(file_path, 'r') as f:
            self.text = f.read()

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

    def persist_xmi(self, file_path):
        with open(file_path, 'w') as f:
            f.write(self.create_xmi_string_from_spacy())

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


def load_ubertext(file_path):
    import bedrock.common
    return bedrock.common.load_pickle(file_path)

if __name__ == '__main__':

    import os as os

    ###to be modified
    file_dir = '/home/achermannr/drivei_nlp_syn/Pathology/TestLabeling/Test/'
    file_names =  [f for f in os.listdir(file_dir) if f.endswith('.txt')]

    for i in range(0,file_names.__len__()):
        utx = Ubertext(file_dir + file_names[i],
                lang='/home/achermannr/nlp_local/library/de_core_news_sm-2.0.0/de_core_news_sm/de_core_news_sm-2.0.0')
        utx.create_xmi_string_from_spacy()
        #utx.persist_xmi('/home/marko/test_xmi.xmi')
        utx.persist_xmi( file_dir + file_names[i].replace('.txt', '.xmi'))

    # TO do Text surrounded with " will not work need to remove beginning and ending "
    # Sentence splitting not good enough?     

