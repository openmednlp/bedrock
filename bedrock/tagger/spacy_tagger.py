from bedrock.doc.doc import Doc
from bedrock.tagger.tagger_if import Tagger
from bedrock.utils import uima
import spacy
import pandas as pd


class SpacyTagger(Tagger):

    def __init__(self, spacy_model_path):
        self.nlp = spacy.load(spacy_model_path)
        self.nlp.add_pipe(self.set_custom_boundaries, before='parser')

    def get_tags(self, doc: Doc):
        spacy_doc = self.nlp(doc.get_text())

        # TODO is_sent_start of spaCy is inconsistent! take care!

        OFFSET = 19

        cols = ['id', 'text', 'begin', 'end', 'is_sent_start', 'pos_value', 'dependency_type', 'governor_id', 'entity']
        tokens = pd.DataFrame(
            [(token_id + OFFSET,
              token.text,
              token.idx,
              token.idx + len(token.text),
              token.is_sent_start, token.pos_, token.dep_, token.head.i + OFFSET,
              "{0}-{1}".format(token.ent_iob_, token.ent_type_) if token.ent_iob_ != 'O' else token.ent_iob_)
             for token_id, token in enumerate(spacy_doc)],
            columns=cols
        )

        # tokens
        annotations = tokens[['id', 'begin', 'end']]  # makes a data frame copy
        annotations.loc[:, 'layer'] = 'token'
        annotations.loc[:, 'feature'] = None  # 'token'
        annotations.loc[:, 'feature_value'] = None  # tokens['id']

        # POS annotations
        pos_annotations = tokens[['begin', 'end']]
        pos_annotations.loc[:, 'layer'] = 'pos'  # type in TypeSystem file, type description name
        pos_annotations.loc[:, 'feature'] = 'pos_value'
        pos_annotations.loc[:, 'feature_value'] = tokens['pos_value']
        annotations = annotations.append(pos_annotations, ignore_index=True)

        # sentence annotations
        sentence_start = tokens['is_sent_start']==True  #
        sentence_start[0] = True
        sentence_annotations = pd.DataFrame(tokens[sentence_start]['begin'].astype(int))  # TODO do we need to use .loc here?
        sentence_annotations.loc[:, 'end'] = sentence_annotations['begin'].shift(-1).fillna(len(doc.get_text())).astype(int) - 1
        sentence_annotations.loc[:, 'layer'] = 'sentence'
        sentence_annotations.loc[:, 'feature'] = None  # 'sentence' TODO unclear
        sentence_annotations.loc[:, 'feature_value'] = None  # list(range(sentence_annotations.shape[0])) TODO unclear

        annotations = annotations.append(sentence_annotations, ignore_index=True)

        # dependencies
        relations = tokens[['begin', 'end', 'governor_id']]
        relations.loc[:, 'layer'] = 'dependency'
        relations.loc[:, 'feature'] = 'dependency_type'
        relations.loc[:, 'feature_value'] = tokens['dependency_type']
        relations.loc[:, 'dependent_id'] = tokens['id']

        return tokens, annotations, relations

    # Overwrite spacy internal boundery function
    def set_custom_boundaries(self, spacydoc):
        for token in spacydoc[:-1]:
            if token.text == ':':
                spacydoc[token.i].is_sent_start = False
        return spacydoc

