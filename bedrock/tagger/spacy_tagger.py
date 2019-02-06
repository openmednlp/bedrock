from bedrock.doc.doc_if import Doc
from bedrock.tagger.tagger_if import Tagger
import spacy
import pandas as pd

class SpacyTagger(Tagger):

    def __init__(self, spacy_model_path):
        self.nlp = spacy.load(spacy_model_path)
        self.nlp.add_pipe(self.set_custom_boundaries, before='parser')

    def get_tags(self, doc: Doc):

        spacy_doc = self.nlp(doc.get_text())

        tokens = pd.DataFrame(
            [(token.text, token.idx, token.idx + len(token.text),
              token.is_sent_start, token.pos_, token.dep_, token_id,
              "{0}-{1}".format(token.ent_iob_, token.ent_type_) if token.ent_iob_ != 'O' else token.ent_iob_,
              token.head.i)
             for token_id, token in enumerate(spacy_doc)],
            columns=['text', 'beg', 'end', 'is_sent_start', 'pos', 'dep', 'id', 'ent', 'gov_id'])

        # tokens
        annotations = tokens[['beg', 'end', 'id']]
        annotations.loc[:, 'layer'] = 'token'
        annotations.loc[:, 'feature'] = 'token'
        annotations.loc[:, 'class'] = tokens['id']
        annotations.loc[:, 'sofa_id'] = 0 # list(range(self.sofa_id, self.sofa_id + annotations.shape[0]))

        # POS annotations
        pos_annotations = tokens[['beg', 'end', 'id']]
        pos_annotations.loc[:, 'layer'] = 'pos'
        pos_annotations.loc[:, 'feature'] = 'pos'
        pos_annotations.loc[:, 'class'] = tokens['pos']
        pos_annotations.loc[:, 'sofa_id'] = 0 # list(range(self.sofa_id, self.sofa_id + pos_annotations.shape[0]))
        annotations = annotations.append(pos_annotations, ignore_index=True)

        # sentence annotations
        sentence_start = tokens['is_sent_start'] == True
        sentence_start[0] = True

        sentence_annotations = pd.DataFrame(tokens[sentence_start]['beg'].astype(int))
        sentence_annotations.loc[:, 'end'] = sentence_annotations['beg'].shift(-1).fillna(len(doc.get_text())).astype(int) - 1
        sentence_annotations.loc[:, 'layer'] = 'sentence'
        sentence_annotations.loc[:, 'feature'] = 'sentence'
        sentence_annotations.loc[:, 'class'] = list(range(sentence_annotations.shape[0]))
        sentence_annotations.loc[:, 'sofa_id'] = 0 # list(range(self.sofa_id, self.sofa_id + sentence_annotations.shape[0]))

        annotations = annotations.append(sentence_annotations, ignore_index=True)

        # dependencies
        relations = tokens[['beg', 'end', 'id']]
        relations.loc[:, 'layer'] = 'dependency'
        relations.loc[:, 'feature'] = 'dependency'
        relations.loc[:, 'class'] = tokens['dep']
        relations.loc[:, 'sofa_id'] = 0 # list(range(self.sofa_id, self.sofa_id + pos_annotations.shape[0]))
        relations.loc[:, 'dep_id'] = tokens['id']
        relations.loc[:, 'gov_id'] = tokens['gov_id']
        relations.loc[:, 'sofa_id'] = 0 # list(range(self.sofa_id, self.sofa_id + relations.shape[0]))

        return tokens, annotations, relations

    # Overwrite spacy internal boundery function
    def set_custom_boundaries(self, spacydoc):
        for token in spacydoc[:-1]:
            if token.text == ':':
                spacydoc[token.i + 1].is_sent_start = False
        return spacydoc

