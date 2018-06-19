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
        self.sofa_id = self.json['_views']['_InitialView']['DocumentMetaData'][0]['sofa']
        self.text = self.json['_referenced_fss'][str(self.sofa_id)]['sofaString']

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

    ## Marko
    ## added for prelabeling
    def __context_enrich(self, custom_layer_name):
        self._context_add_type(custom_layer_name)
        self._context_add_type_subtype('Annotation', custom_layer_name)

    def _context_add_type(self, type_name, feature_types={'sofa': '_ref'}):
        self.json['_context']['_types'][type_name] = {'_feature_types': feature_types}

    def _context_add_type_subtype(self, type_name, subtype_name):
        self.json['_context']['_types'][type_name]['_subtypes'].append(subtype_name)

    def __views_enrich(self, custom_layer_name):
        init_view = self.json['_views']['_InitialView']
        init_view['TagsetDescription'].append({
            'sofa': self.sofa_id,
            'layer': ''.join(['webanno.custom.', custom_layer_name]),
            'name': ''.join([custom_layer_name, ' prelabeling'])
        })
        # TODO: add depencecies
        return 0

    def __referenced_fss_enrich(self, custom_layer_name, prelabeling_results):
        # TODO test this
        fss_id = max(self.json['_referenced_fss'].keys(), key=int) + 1
        for res in prelabeling_results:
            self.json['_referenced_fss'][fss_id] = {
                "_type": custom_layer_name,
                "sofa": self.sofa_id,
                "begin": res.begin,
                "end": res.end,
                "TODO": "TODO"}
            id += 1

    def json_enrich(self, custom_layer_name, prelabeling_results):
        self.__context_enrich(custom_layer_name)
        self.__referenced_fss_enrich(custom_layer_name, prelabeling_results)
        self.__views_enrich(custom_layer_name, prelabeling_results) # TODO check here if



def load_ubertext(file_path):
    import bedrock.common
    return bedrock.common.load_pickle(file_path)


if __name__ == '__main__':
    file_path = '/home/marko/Downloads/USB0002055664_24213774.json'
    utx = Ubertext(file_path)

    # TODO realize, this is just mocking code
    # tnm_prelabeling = bedrock.prelabeling.Prelabeling('TNM')
    # prelabeling_results = tnm_prelabeling.run(self.text)
    # custom_layer_name = 'TNM'
    # utx.json_enrich(custom_layer_name, prelabeling_results)
