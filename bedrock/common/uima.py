from enum import Enum
# TODO use TypeSystem as better alternative to assigne to set the correct values

BEGIN = 'begin'
END = 'end'


class StandardTypeNames(Enum):

    SENTENCE = 'de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Sentence'

    TOKEN = 'de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token'

    POS = 'de.tudarmstadt.ukp.dkpro.core.api.lexmorph.type.pos.POS'

    DEPENDENCY = 'de.tudarmstadt.ukp.dkpro.core.api.syntax.type.dependency.Dependency'


class CustomTypeNames(Enum):

    TUMOR = 'webanno.custom.Tumor'


class DependencyFeatureNames(Enum):

    GOVERNOR = 'Governor'

    DEPENDENT = 'Dependent'

    DEPENDENCY_TYPE = 'DependencyType'


class PosFeatureNames(Enum):

    POS_VALUE = 'PosValue'
