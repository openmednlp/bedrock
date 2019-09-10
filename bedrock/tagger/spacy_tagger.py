from bedrock.doc.doc import Doc
from bedrock.doc.layer import Layer
from bedrock.doc.relation import Relation
from bedrock.doc.annotation import Annotation
from bedrock.doc.token import Token
from bedrock.tagger.tagger import Tagger
import spacy
import pandas as pd


class SpacyTagger(Tagger):

    ID_OFFSET = 19

    def __init__(self, language='de'):
        self.nlp = spacy.load(language)
        self.nlp.add_pipe(self.set_custom_boundaries, before='parser')

    def nlp(self, text: str):
        return self.nlp(text)

    def get_tags(self, doc: Doc):
        spacy_doc = self.nlp(doc.get_text())

        tokens = pd.DataFrame(
            [(token_id,
              token.idx,
              token.idx + len(token.text),
              token.text,
              token.is_sent_start,
              token.pos_,
              token.dep_,
              token.head.i,
              "{0}-{1}".format(token.ent_iob_, token.ent_type_) if token.ent_iob_ != 'O' else token.ent_iob_)
             for token_id, token in enumerate(spacy_doc)],
            columns=Token.COLS
        )

        annotations = self.create_annotations_from_tokens(tokens)
        pos_annotations = self.create_annotations_from_pos(tokens)
        annotations = annotations.append(pos_annotations, ignore_index=True)  # index will be auto-increment

        sentence_annotations = self.create_annotations_from_sentences(doc, tokens)
        annotations = annotations.append(sentence_annotations, ignore_index=True)  # index will be auto-increment

        last_index_annotations = annotations.index[-1]
        relations = self.create_dependency_relations_from_tokens(tokens)
        relations.index += (last_index_annotations+1)

        annotations.index += self.ID_OFFSET
        relations.index += self.ID_OFFSET
        relations[[Relation.GOV_ID, Relation.DEP_ID]] += self.ID_OFFSET

        return tokens, annotations, relations

    def create_dependency_relations_from_tokens(self, tokens):
        # dependencies
        relations = tokens[[Token.BEGIN, Token.END, Relation.GOV_ID]]
        relations.loc[:, Relation.LAYER] = Layer.DEPENDENCY
        relations.loc[:, Relation.FEATURE] = Token.DEP_TYPE
        relations.loc[:, Relation.FEATURE_VAL] = tokens[Token.DEP_TYPE]
        relations.loc[:, Relation.DEP_ID] = tokens[Token.ID]
        return relations

    def create_annotations_from_sentences(self, doc, tokens):
        # sentence annotations --> has no ID col
        sentence_start = tokens[Token.SENT_START] == True
        sentence_start[0] = True
        sentence_annotations = pd.DataFrame(
            tokens[sentence_start][Token.BEGIN].astype(int))  # TODO do we need to use .loc here?
        sentence_annotations.loc[:, Annotation.END] = sentence_annotations[Annotation.BEGIN].shift(-1).fillna(
            len(doc.get_text())).astype(int) - 1
        sentence_annotations.loc[:, Annotation.LAYER] = Layer.SENTENCE
        sentence_annotations.loc[:, Annotation.FEATURE] = None  # 'sentence' TODO unclear if ok?
        sentence_annotations.loc[:, Annotation.FEATURE_VAL] = None  # TODO unclear if ok?
        return sentence_annotations

    def create_annotations_from_pos(self, tokens):
        # pos annotations --> has no ID col
        pos_annotations = tokens[[Token.BEGIN, Token.END]]
        pos_annotations.loc[:, Annotation.LAYER] = Layer.POS  # type in TypeSystem file, type description name
        pos_annotations.loc[:, Annotation.FEATURE] = Token.POS_VALUE
        pos_annotations.loc[:, Annotation.FEATURE_VAL] = tokens[Token.POS_VALUE]
        return pos_annotations

    def create_annotations_from_tokens(self, tokens: pd.DataFrame):
        annotations = tokens[[Token.BEGIN, Token.END]]
        annotations.loc[:, Annotation.LAYER] = Layer.TOKEN
        annotations.loc[:, Annotation.FEATURE] = Token.TEXT
        annotations.loc[:, Annotation.FEATURE_VAL] = tokens[Token.TEXT]
        return annotations

    # Overwrite spacy internal boundery function
    def set_custom_boundaries(self, spacydoc):
        for token in spacydoc[:-1]:
            if token.text == ':':
                spacydoc[token.i].is_sent_start = False
        return spacydoc

