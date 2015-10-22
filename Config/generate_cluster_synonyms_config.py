from config_base import ConfigurationBase

class GenerateClusterSynonymsConfig(ConfigurationBase):

    def __init__(self, fname):
        ConfigurationBase.__init__(self, fname)

        self.keywords_files = self.__getstring__("DEFAULT", "keyword_files").split(",")
        self.num_clusters          = self.__getint__("DEFAULT", "num_clusters")
        self.model_file     = self.__getstring__("DEFAULT", "word2vec_model_file")
        self.synonyms_file  = self.__getstring__("DEFAULT", "synonyms_file")