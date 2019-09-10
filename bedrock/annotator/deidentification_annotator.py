from bedrock.annotator.annotator import Annotator
from bedrock.doc.doc import Doc
from doc.annotation import Annotation
from bedrock.common.deiditificatior import Deidentificator
import pandas as pd
import re


class DeidentificationAnnotator(Annotator):

	def __init__(self, layer_name: str, lastnames: List, prenames: List, postcodes: List, street_names: List=[], city_names: List=[]):
		self.__ = patterns
		self.__layer_name = layer_name
		self.__deidentificator = Deidentificator(lastnames, prenames, postcodes, street_names=street_names, city_names=city_names)

	def get_annotations(self, doc: Doc) -> (pd.DataFrame, pd.DataFrame):
		annotations = pd.DataFrame()
		relations = pd.DataFrame()
		patient_lastname = None
		patient_prenams = None
		if doc.has_meta_key('patient_lastname'):
			patient_lastname = doc.get_meta_data('patient_lastname')
		if doc.has_meta_key('patient_prenames'):
			patient_prenames = doc.get_meta_data('patient_prenames').split(' ')
		substitutions = self.__deidentificator.detect_identifiers(patient_prenames, doc.get_text(), patient_lastname)
		for idx, row in substitutions.iterrows():
			annotations = annotations.append({
				Annotation.BEGIN: row['start'],
				Annotation.END: row['end'],
				Annotation.LAYER: self.__layer_name,
				Annotation.FEATURE: row['type'],
				Annotation.FEATURE_VAL: row['span'],
			}, ignore_index=True)

		return annotations, relations
