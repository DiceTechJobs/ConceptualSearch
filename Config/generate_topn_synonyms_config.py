from config_base import ConfigurationBase

class GenerateTopNSynonymsConfig(ConfigurationBase):

    def __init__(self, fname):
        ConfigurationBase.__init__(self, fname)

        self.keywords_files = self.__getstring__("DEFAULT", "keyword_files").split(",")
        self.top_n          = self.__getint__("DEFAULT", "top_n")
        self.model_file     = self.__getstring__("DEFAULT", "word2vec_model_file")
        self.payload_synonyms_file  = self.__getstring__("DEFAULT", "payload_synonyms_file")
        self.synonyms_file  = self.__getstring__("DEFAULT", "synonyms_file")