from bedrock.doc.doc import Doc
from xml.sax import saxutils
from pycas.cas.core.CasFactory import CasFactory
from common.cas2df import CAS2DataFrameConverter


class DocFactory:

    @staticmethod
    def create_doc_from_text(text: str, filename: str) -> Doc:
        doc = Doc()
        doc.set_filename(filename)
        doc.set_text(DocFactory.__preprocess(text))
        return doc

    @staticmethod
    def create_doc_from_xmi(xmi_content: str, type_content: str, xmi_filename: str) -> Doc:
        doc = Doc()
        doc.set_filename(xmi_filename)
        cas = CasFactory().buildCASfromStrings(xmi_content, type_content)
        tokens, annotations, relations = CAS2DataFrameConverter.get_dataframes(cas)
        doc.set_text(cas.documentText)
        doc.set_tokens(tokens)
        doc.set_annotations(annotations)
        doc.set_relations(relations)
        return doc

    @staticmethod
    def __preprocess(text_raw: str) -> str:
        """ argument text_raw: string
            returns text_proproc: processed string in utf_8 format, escaped
            """
        # preprocess such that webanno and spacy text the same, no changes in Webanno
        # side effect: lose structure of report (newline)
        text_preproc = text_raw

        # utf-8 encoding
        text_preproc = text_preproc.strip('"')
        text_preproc = text_preproc.replace("\n", " ")
        text_preproc = text_preproc.replace("<br>", "\n")
        text_preproc = ' '.join(filter(len, text_preproc.split(' ')))
        text_preproc = saxutils.unescape(text_preproc)
        return text_preproc




