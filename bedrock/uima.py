import json
import spacy


class Ubertext():
    def __init__(self, file_path, lang='de'):
        # TODO: check if file type JSON
        print(file_path)

        self.__set_json(file_path)
        self.__set_text()

        nlp = spacy.load(lang)
        self.spacy = nlp(self.__str__())

    def __set_text(self):
        sofa_id = self.json['_views']['_InitialView']['DocumentMetaData'][0]['sofa']
        self.text = self.json['_referenced_fss'][str(sofa_id)]['sofaString']

    def __set_json(self, file_path):
        with open(file_path, 'r') as f:
            self.json = json.load(f)

    def __str__(self):
        s = self.json['_views']['_InitialView']['DocumentMetaData'][0]['sofa']
        full_text = self.json['_referenced_fss'][str(s)]['sofaString']
        return full_text

    def __repr__(self):
        full_text = self.__str__()
        doc_metadata = self.json['_views']['_InitialView']['DocumentMetaData'][0]
        return (
            ' - Short info - \n' +
            '\nTitle: ' + doc_metadata['documentTitle'] +
            '\nId: ' + doc_metadata['documentId'] +
            '\n\nFull string:\n' + full_text
        )

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
    file_path = '/home/giga/dev/python/bedrock/bedrock/data/uima.json'
    utx = Ubertext(file_path)

    print(utx)