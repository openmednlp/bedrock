from bedrock.tagger.spacy_tagger import SpacyTagger
from bedrock.doc.doc_factory import DocFactory
from bedrock.prelabel.annotator import Annotator
from bedrock.doc.relation import Relation


class Pipeline:
    def __init__(self, language='en'):
        # set tagger language
        self._language = 'xx_ent_wiki_sm'
        if language == 'en':
            self._language = 'en_core_web_md'
        elif language == 'de':
            self._language = 'de_core_news_md'
        elif language == 'fr':
            self._language = 'fr_core_news_md'

        self._docs = []
        self._tagger = SpacyTagger(language=self._language)
        self._annotators = []
        self._post_labeling_annotators = []
        self._doc_factory = DocFactory()

    def clear(self):
        self._docs = []
        self._annotators = []
        self._post_labeling_annotators = []
        self._doc_factory = DocFactory()
        return self

    def get_docs(self):
        return self._docs

    def parse_text(self, text: str):
        doc = self._doc_factory.create_doc_from_text(text, None)
        self._docs.append(doc)
        return self

    def parse_cas(self, xmi_file_path: str, type_system_file_path: str):
        doc = self._doc_factory.create_doc_from_xmi_path(xmi_file_path, type_system_file_path)
        self._docs.append(doc)
        return self

    def set_tags(self):
        if self._tagger is not None:
            for doc in self._docs:
                tokens, annotations, relations = self._tagger.get_tags(doc)
                doc.set_tokens(tokens)
                doc.set_annotations(annotations)
                doc.set_relations(relations)
        return self

    def set_annotator(self, annotator: Annotator):
        self._annotators.append(annotator)

    def set_post_labeling_annotator(self, annotator: Annotator):
        self._post_labeling_annotators.append(annotator)

    def set_annotations(self):
        for doc in self._docs:
            for annotator in self._annotators:
                annotations, relations = annotator.get_annotations(doc)
                next_index = doc.get_next_start_index()  # returns 0 if doc.__annotations empty
                if not annotations.empty:
                    annotations.index += next_index
                    max_annotations_index = annotations.index[-1]
                    doc.append_annotations(annotations, False)
                    if not relations.empty:  # relations cannot exist without annotations
                        relations[[Relation.GOV_ID, Relation.DEP_ID]] += next_index
                        relations.index += max_annotations_index + 1
                        doc.append_relations(relations, False)
        return self

    def run_post_labeling(self):
        for doc in self._docs:
            for post_annotator in self._post_labeling_annotators:
                annotations, relations = post_annotator.get_annotations(doc)
                doc.set_annotations(annotations)
                if relations is not None:
                    doc.set_relations(relations)
        return self

    def process(self):
        return self.set_tags().set_annotations().run_post_labeling()
