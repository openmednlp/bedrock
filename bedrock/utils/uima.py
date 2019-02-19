
# TODO use TypeSystem as better alternative to assigne to set the correct values


class StandardTypeNames:

    SENTENCE = 'de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Sentence'

    TOKEN = 'de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token'

    POS = 'de.tudarmstadt.ukp.dkpro.core.api.lexmorph.type.pos.POS'

    DEPENDENCY = 'de.tudarmstadt.ukp.dkpro.core.api.syntax.type.dependency.Dependency'


class CustomTypeNames:

    TUMOR = 'webanno.custom.Tumor'


class DependencyFeatureNames:

    GOVERNOR = 'Governor'

    DEPENDENT = 'Dependent'

    DEPENDENCY_TYPE = 'DependencyType'


class PosFeatureNames:

    POS_VALUE = 'PosValue'