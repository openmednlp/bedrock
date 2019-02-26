from bedrock.doc.doc import Doc, Token, Annotation, Layer, Relation
from bedrock.tagger.tagger_if import Tagger
import spacy
import pandas as pd


class SpacyTagger(Tagger):

    ID_OFFSET = 19

    def __init__(self, spacy_model_path):
        self.nlp = spacy.load(spacy_model_path)
        self.nlp.add_pipe(self.set_custom_boundaries, before='parser')

    def get_tags(self, doc: Doc):
        spacy_doc = self.nlp(doc.get_text())

        # TODO is_sent_start of spaCy is inconsistent! take care!

        tokens = pd.DataFrame(
            [(token_id + self.ID_OFFSET,
              token.idx,
              token.idx + len(token.text),
              token.text,
              token.is_sent_start, token.pos_, token.dep_, token.head.i + self.ID_OFFSET,
              "{0}-{1}".format(token.ent_iob_, token.ent_type_) if token.ent_iob_ != 'O' else token.ent_iob_)
             for token_id, token in enumerate(spacy_doc)],
            columns=Token.COLS
        )

        # tokens
        annotations = tokens[[Token.ID, Token.BEGIN, Token.END]]  # makes a data frame copy
        annotations.loc[:, Annotation.LAYER] = Layer.TOKEN
        annotations.loc[:, Annotation.FEATURE] = None  # 'token' TODO unclear if ok?
        annotations.loc[:, Annotation.FEATURE_VAL] = None  # tokens['id'] TODO unclear if ok?

        # pos annotations
        pos_annotations = tokens[[Token.BEGIN, Token.END]]
        pos_annotations.loc[:, Annotation.LAYER] = Layer.POS  # type in TypeSystem file, type description name
        pos_annotations.loc[:, Annotation.FEATURE] = Token.POS_VALUE
        pos_annotations.loc[:, Annotation.FEATURE_VAL] = tokens[Token.POS_VALUE]
        annotations = annotations.append(pos_annotations, ignore_index=True)

        # sentence annotations
        sentence_start = tokens[Token.SENT_START]==True
        sentence_start[0] = True
        sentence_annotations = pd.DataFrame(tokens[sentence_start][Token.BEGIN].astype(int)) # TODO do we need to use .loc here?
        sentence_annotations.loc[:, Annotation.END] = sentence_annotations[Annotation.BEGIN].shift(-1).fillna(len(doc.get_text())).astype(int) - 1
        sentence_annotations.loc[:, Annotation.LAYER] = Layer.SENT
        sentence_annotations.loc[:, Annotation.FEATURE] = None  # 'sentence' TODO unclear if ok?
        sentence_annotations.loc[:, Annotation.FEATURE_VAL] = None # TODO unclear if ok?

        annotations = annotations.append(sentence_annotations, ignore_index=True)

        # dependencies
        relations = tokens[[Token.BEGIN, Token.END, Relation.GOV_ID]]
        relations.loc[:, Relation.LAYER] = Layer.DEP
        relations.loc[:, Relation.FEATURE] = Token.DEP_TYPE
        relations.loc[:, Relation.FEATURE_VAL] = tokens[Token.DEP_TYPE]
        relations.loc[:, Relation.DEP_ID] = tokens[Token.ID]

        return tokens, annotations, relations

    # Overwrite spacy internal boundery function
    def set_custom_boundaries(self, spacydoc):
        for token in spacydoc[:-1]:
            if token.text == ':':
                spacydoc[token.i].is_sent_start = False
        return spacydoc

