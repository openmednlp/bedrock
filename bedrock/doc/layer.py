from common import utils, uima


class Layer:
    TOKEN = utils.get_layer_name(uima.StandardTypeNames.TOKEN)
    POS = utils.get_layer_name(uima.StandardTypeNames.POS)
    SENTENCE = utils.get_layer_name(uima.StandardTypeNames.SENTENCE)
    DEPENDENCY = utils.get_layer_name(uima.StandardTypeNames.DEPENDENCY)
    TUMOR = utils.get_layer_name(uima.CustomTypeNames.TUMOR)
    TUMOR_RELATION = utils.get_layer_name(uima.CustomTypeNames.TUMOR_REL)